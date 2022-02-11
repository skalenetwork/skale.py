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

import logging
import functools
from dataclasses import dataclass

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes
from web3.exceptions import ContractLogicError


logger = logging.getLogger(__name__)


NO_PREVIOUS_NODE_EXCEPTION_TEXT = 'No previous node'


@dataclass
class Rotation:
    leaving_node_id: int
    new_node_id: int
    freeze_until: int
    rotation_counter: int


class NodeRotation(BaseContract):
    """Wrapper for NodeRotation.sol functions"""

    @property
    @functools.lru_cache()
    def schains(self):
        return self.skale.schains

    def get_rotation_obj(self, schain_name) -> Rotation:
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
            'freeze_until': rotation_data[2],
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
        finish_ts = next(
            (schain[1] for schain in raw_history if '0x' + schain[0].hex() == schain_id), None)
        if not finish_ts:
            return None
        exception = self.skale.schains_internal.check_exception(schain_name, node_id)
        if exception:
            rotation_delay = self.skale.constants_holder.get_rotation_delay()
            logger.info(f'Node {node_id} in exceptions array for {schain_name}, \
adding {rotation_delay} to {finish_ts}.')
            finish_ts += rotation_delay
        return finish_ts

    def is_rotation_in_progress(self, schain_name) -> bool:
        schain_id = self.schains.name_to_id(schain_name)
        return self.contract.functions.isRotationInProgress(schain_id).call()

    def is_new_node_found(self, schain_name) -> bool:
        schain_id = self.schains.name_to_id(schain_name)
        return self.contract.functions.isNewNodeFound(schain_id).call()

    def is_rotation_active(self, schain_name) -> bool:
        """
        The public function that tells whether rotation is in the active phase - the new group is
        already generated
        """
        return self.is_rotation_in_progress(schain_name) and self.is_new_node_found(schain_name)

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
