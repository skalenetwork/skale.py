#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019-Present SKALE Labs
#
#   SKALE.py is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   SKALE.py is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with SKALE.py.  If not, see <https://www.gnu.org/licenses/>.
""" NodeRotation.sol functions """

import functools
from dataclasses import dataclass
from collections import namedtuple

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes
from web3.exceptions import ContractLogicError


NO_PREVIOUS_NODE_EXCEPTION_TEXT = 'No previous node'


@dataclass
class Rotation:
    node_id: int
    new_node_id: int
    freeze_until: int
    rotation_counter: int


RotationNodeData = namedtuple('RotationNodeData', ['index', 'node_id', 'public_key'])


class NodeRotation(BaseContract):
    """Wrapper for NodeRotation.sol functions"""

    @property
    @functools.lru_cache()
    def schains(self):
        return self.skale.schains

    def get_rotation_obj(self, schain_name):
        schain_id = self.schains.name_to_id(schain_name)
        rotation_data = self.contract.functions.getRotation(schain_id).call()
        return Rotation(*rotation_data)

    def get_rotation(self, schain_name):
        print('WARNING: Deprecated, will be removed in v6')
        schain_id = self.schains.name_to_id(schain_name)
        rotation_data = self.contract.functions.getRotation(schain_id).call()
        return {
            'leaving_node': rotation_data[0],
            'new_node': rotation_data[1],
            'finish_ts': rotation_data[2],
            'rotation_id': rotation_data[3]
        }

    def get_leaving_history(self, node_id):
        raw_history = self.contract.functions.getLeavingHistory(node_id).call()
        history = [
            {
                'schain_id': schain[0],
                'finished_rotation': schain[1]
            }
            for schain in raw_history
        ]
        return history

    def get_schain_finish_ts(self, node_id: int, schain_name: str) -> int:
        raw_history = self.contract.functions.getLeavingHistory(node_id).call()
        schain_id = self.skale.schains.name_to_id(schain_name)
        return next(
            (schain[1] for schain in raw_history if '0x' + schain[0].hex() == schain_id), None)

    def is_rotation_in_progress(self, schain_name):
        schain_id = self.schains.name_to_id(schain_name)
        return self.contract.functions.isRotationInProgress(schain_id).call()

    def wait_for_new_node(self, schain_name):
        schain_id = self.schains.name_to_id(schain_name)
        return self.contract.functions.waitForNewNode(schain_id).call()

    @transaction_method
    def grant_role(self, role: bytes, owner: str) -> TxRes:
        return self.contract.functions.grantRole(role, owner)

    def has_role(self, role: bytes, address: str) -> bool:
        return self.contract.functions.hasRole(role, address).call()

    def debugger_role(self):
        return self.contract.functions.DEBUGGER_ROLE().call()

    def get_previous_node(self, schain_name: str, node_id: int) -> int:
        schain_id = self.schains.name_to_id(schain_name)
        try:
            return self.contract.functions.getPreviousNode(schain_id, node_id).call()
        except ContractLogicError as e:
            if NO_PREVIOUS_NODE_EXCEPTION_TEXT in str(e):
                return None
            raise e

    def _compose_bls_public_key_info(self, bls_public_key: str):  # TODO: move!
        return {
            'blsPublicKey0': str(bls_public_key[0][0]),
            'blsPublicKey1': str(bls_public_key[0][1]),
            'blsPublicKey2': str(bls_public_key[1][0]),
            'blsPublicKey3': str(bls_public_key[1][1])
        }

    def get_previous_nodes(self, schain_name: str) -> list:
        """
        Returns all previous node groups with public keys and finish timestamps
        """
        node_groups = {}
        current_nodes = {}

        group_id = self.skale.schains.name_to_group_id(schain_name)
        previous_public_keys = self.skale.key_storage.get_all_previous_public_keys(group_id)

        rotation = self.get_rotation_obj(schain_name)

        # get current state

        ids = self.skale.schains_internal.get_node_ids_for_schain(schain_name)
        for (index, node_id) in enumerate(ids):
            public_key = self.skale.nodes.get_node_public_key(node_id)
            current_nodes[node_id] = RotationNodeData(index, node_id, public_key)

        node_groups[rotation.rotation_counter] = {
            'nodes': current_nodes,
            'finish_ts': None,
            'bls_public_key': 22222222222  # todo <- current bls key!
        }

        if rotation.rotation_counter == 0:
            return node_groups

        # handle last rotation manually

        latest_rotation_nodes = current_nodes.copy()
        public_key = self.skale.nodes.get_node_public_key(rotation.node_id)

        latest_rotation_nodes[rotation.node_id] = RotationNodeData(
            current_nodes[rotation.new_node_id].index,
            rotation.node_id,
            public_key
        )
        del latest_rotation_nodes[rotation.new_node_id]
        node_groups[rotation.rotation_counter - 1] = {
            'nodes': latest_rotation_nodes,
            'finish_ts': rotation.freeze_until,
            'bls_public_key': self._compose_bls_public_key_info(previous_public_keys[rotation.rotation_counter - 1]) # noqa
        }

        if rotation.rotation_counter == 1:
            return node_groups

        # handle other rotations in loop

        previous_nodes = {}

        for rotation_id in range(rotation.rotation_counter - 2, -1, -1):
            nodes = node_groups[rotation_id + 1]['nodes'].copy()

            for node_id in nodes:
                if node_id not in previous_nodes:
                    previous_node = self.get_previous_node(schain_name, node_id)
                    if previous_node:
                        finish_ts = self.get_schain_finish_ts(previous_node, schain_name)
                        previous_nodes[node_id] = {
                            'finish_ts': finish_ts,
                            'previous_node_id': previous_node
                        }

            latest_exited_node_id = max(previous_nodes, key=previous_nodes.get('finish_ts'))
            previous_node_id = previous_nodes[latest_exited_node_id]['previous_node_id']
            public_key = self.skale.nodes.get_node_public_key(previous_node_id)

            nodes[previous_node_id] = RotationNodeData(
                nodes[latest_exited_node_id].index,
                previous_node_id,
                public_key
            )
            del nodes[latest_exited_node_id]

            node_groups[rotation_id] = {
                'nodes': nodes,
                'finish_ts': previous_nodes[latest_exited_node_id]['finish_ts'],
                'bls_public_key': self._compose_bls_public_key_info(previous_public_keys[rotation_id]) # noqa
            }

            del previous_nodes[latest_exited_node_id]

        return node_groups
