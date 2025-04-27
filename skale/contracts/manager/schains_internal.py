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
"""SchainsInternal.sol functions"""

import functools
from typing import TYPE_CHECKING, List

from eth_typing import ChecksumAddress

from skale.contracts.base_contract import transaction_method
from skale.contracts.skale_manager_contract import SkaleManagerContract
from skale.types.node import NodeId
from skale.types.schain import Schain, SchainHash, SchainName

if TYPE_CHECKING:
    from web3.contract.contract import ContractFunction
    from skale.contracts.manager.schains import SChains


class SChainsInternal(SkaleManagerContract):
    """Wrapper for some of the SchainsInternal.sol functions"""

    @property
    @functools.lru_cache()
    def schains(self) -> 'SChains':
        return self.skale.schains

    def get_raw(self, name: SchainHash) -> Schain:
        return Schain(*self.contract.functions.schains(name).call())

    def get_all_schains_ids(self) -> List[SchainHash]:
        return [
            SchainHash(schain_hash) for schain_hash in self.contract.functions.getSchains().call()
        ]

    def get_schains_number(self) -> int:
        return int(self.contract.functions.numberOfSchains().call())

    def get_schain_list_size(self, account: ChecksumAddress) -> int:
        return int(self.contract.functions.getSchainListSize(account).call({'from': account}))

    def get_schain_id_by_index_for_owner(self, account: ChecksumAddress, index: int) -> SchainHash:
        return SchainHash(self.contract.functions.schainIndexes(account, index).call())

    def get_node_ids_for_schain(self, name: SchainName) -> List[NodeId]:
        id_ = self.schains.name_to_id(name)
        return [NodeId(node) for node in self.contract.functions.getNodesInGroup(id_).call()]

    def get_schain_ids_for_node(self, node_id: NodeId) -> List[SchainHash]:
        return [
            SchainHash(schain)
            for schain in self.contract.functions.getSchainHashesForNode(node_id).call()
        ]

    def is_schain_exist(self, name: SchainName) -> bool:
        id_ = self.schains.name_to_id(name)
        return bool(self.contract.functions.isSchainExist(id_).call())

    def get_active_schain_ids_for_node(self, node_id: NodeId) -> List[SchainHash]:
        return [
            SchainHash(schain)
            for schain in self.contract.functions.getActiveSchains(node_id).call()
        ]

    def number_of_schain_types(self) -> int:
        return int(self.contract.functions.numberOfSchainTypes().call())

    @transaction_method
    def add_schain_type(self, part_of_node: int, number_of_nodes: int) -> 'ContractFunction':
        return self.contract.functions.addSchainType(part_of_node, number_of_nodes)

    def current_generation(self) -> int:
        return int(self.contract.functions.currentGeneration().call())

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> 'ContractFunction':
        return self.contract.functions.grantRole(role, address)

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.hasRole(role, address).call())

    def schain_type_manager_role(self) -> bytes:
        return bytes(self.contract.functions.SCHAIN_TYPE_MANAGER_ROLE().call())

    def debugger_role(self) -> bytes:
        return bytes(self.contract.functions.DEBUGGER_ROLE().call())

    def generation_manager_role(self) -> bytes:
        return bytes(self.contract.functions.GENERATION_MANAGER_ROLE().call())

    @transaction_method
    def new_generation(self) -> 'ContractFunction':
        return self.contract.functions.newGeneration()

    def check_exception(self, schain_name: SchainName, node_id: NodeId) -> bool:
        id_ = self.schains.name_to_id(schain_name)
        return bool(self.contract.functions.checkException(id_, node_id).call())
