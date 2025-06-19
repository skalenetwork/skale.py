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
"""NodeRotation.sol functions"""

from __future__ import annotations
import logging
import functools
from typing import TYPE_CHECKING, List

from eth_typing import ChecksumAddress

from skale.contracts.base_contract import transaction_method
from web3.contract.contract import ContractFunction
from web3.exceptions import ContractLogicError

from skale.contracts.skale_manager_contract import SkaleManagerContract
from skale.types.node import NodeId
from skale.types.rotation import Rotation, RotationSwap
from skale.types.schain import SchainHash, SchainName

if TYPE_CHECKING:
    from skale.contracts.manager.schains import SChains


logger = logging.getLogger(__name__)


NO_PREVIOUS_NODE_EXCEPTION_TEXT = 'No previous node'


class NodeRotation(SkaleManagerContract):
    """Wrapper for NodeRotation.sol functions"""

    @property
    @functools.lru_cache()
    def schains(self) -> SChains:
        return self.skale.schains

    def get_rotation(self, schain_name: SchainName) -> Rotation:
        schain_id = self.schains.name_to_id(schain_name)
        rotation_data = self.contract.functions.getRotation(schain_id).call()
        return Rotation(*rotation_data)

    def get_leaving_history(self, node_id: NodeId) -> List[RotationSwap]:
        raw_history = self.contract.functions.getLeavingHistory(node_id).call()
        history = [
            RotationSwap({'schain_id': SchainHash(schain[0]), 'finished_rotation': int(schain[1])})
            for schain in raw_history
        ]
        return history

    def get_schain_finish_ts(self, node_id: NodeId, schain_name: SchainName) -> int | None:
        history = self.get_leaving_history(node_id)
        schain_id = self.skale.schains.name_to_id(schain_name)
        finish_ts = next(
            (swap['finished_rotation'] for swap in history if swap['schain_id'] == schain_id), None
        )
        if not finish_ts:
            return None
        return int(finish_ts)

    def is_rotation_in_progress(self, schain_name: SchainName) -> bool:
        schain_id = self.schains.name_to_id(schain_name)
        return bool(self.contract.functions.isRotationInProgress(schain_id).call())

    def is_new_node_found(self, schain_name: SchainName) -> bool:
        schain_id = self.schains.name_to_id(schain_name)
        return bool(self.contract.functions.isNewNodeFound(schain_id).call())

    def is_rotation_active(self, schain_name: SchainName) -> bool:
        """
        The public function that tells whether rotation is in the active phase - the new group is
        already generated
        """
        finish_ts_reached = self.is_finish_ts_reached(schain_name)
        return self.is_rotation_in_progress(schain_name) and not finish_ts_reached

    def is_finish_ts_reached(self, schain_name: SchainName) -> bool:
        rotation = self.skale.node_rotation.get_rotation(schain_name)
        schain_finish_ts = self.get_schain_finish_ts(rotation.leaving_node_id, schain_name)

        if not schain_finish_ts:
            schain_finish_ts = 0

        latest_block = self.skale.web3.eth.get_block('latest')
        current_ts = latest_block['timestamp']

        logger.info(f'current_ts: {current_ts}, schain_finish_ts: {schain_finish_ts}')
        return current_ts > schain_finish_ts

    def wait_for_new_node(self, schain_name: SchainName) -> bool:
        schain_id = self.schains.name_to_id(schain_name)
        return bool(self.contract.functions.waitForNewNode(schain_id).call())

    @transaction_method
    def grant_role(self, role: bytes, owner: str) -> 'ContractFunction':
        return self.contract.functions.grantRole(role, owner)

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.hasRole(role, address).call())

    def debugger_role(self) -> bytes:
        return bytes(self.contract.functions.DEBUGGER_ROLE().call())

    def get_previous_node(self, schain_name: SchainName, node_id: NodeId) -> NodeId | None:
        schain_id = self.schains.name_to_id(schain_name)
        try:
            return NodeId(self.contract.functions.getPreviousNode(schain_id, node_id).call())
        except (ContractLogicError, ValueError) as e:
            if NO_PREVIOUS_NODE_EXCEPTION_TEXT in str(e):
                return None
            raise e
