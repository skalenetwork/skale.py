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
"""Schains.sol functions"""

import functools
from dataclasses import asdict
from typing import Any, List

from Crypto.Hash import keccak
from eth_typing import ChecksumAddress, HexStr
from hexbytes import HexBytes
from web3 import Web3
from web3.contract.contract import ContractFunction
from web3.types import Wei

from skale.contracts.base_contract import transaction_method
from skale.contracts.manager.node_rotation import NodeRotation
from skale.contracts.manager.schains_internal import SChainsInternal
from skale.contracts.skale_manager_contract import SkaleManagerContract
from skale.types.node import NodeId
from skale.types.schain import (
    SchainHash,
    SchainName,
    SchainStructure,
    SchainStructureWithStatus,
)
from skale.dataclasses.schain_options import (
    SchainOptions,
    get_default_schain_options,
    parse_schain_options,
)


class SChains(SkaleManagerContract):
    """Wrapper for some of the Schains.sol functions"""

    def name_to_group_id(self, name: SchainName) -> HexBytes:
        return self.skale.web3.keccak(text=name)

    @property
    @functools.lru_cache()
    def schains_internal(self) -> SChainsInternal:
        return self.skale.schains_internal

    @property
    @functools.lru_cache()
    def node_rotation(self) -> NodeRotation:
        return self.skale.node_rotation

    def get(self, id_: SchainHash) -> SchainStructure:
        res = self.schains_internal.get_raw(id_)
        options = self.get_options(id_)
        return SchainStructure(**asdict(res), chain_id=self.name_to_id(res.name), options=options)

    def get_by_name(self, name: SchainName) -> SchainStructure:
        id_ = self.name_to_id(name)
        return self.get(id_)

    def get_schains_for_owner(self, account: ChecksumAddress) -> List[SchainStructure]:
        schains = []
        list_size = self.schains_internal.get_schain_list_size(account)

        for i in range(0, list_size):
            id_ = self.schains_internal.get_schain_id_by_index_for_owner(account, i)
            schain = self.get(id_)
            schains.append(schain)
        return schains

    def get_schains_for_node(self, node_id: NodeId) -> list[SchainStructureWithStatus]:
        schains = []
        schain_ids = self.schains_internal.get_schain_ids_for_node(node_id)
        for schain_id in schain_ids:
            simple_schain = self.get(schain_id)
            schain = SchainStructureWithStatus(
                **asdict(simple_schain), active=self.schain_active(simple_schain)
            )
            schains.append(schain)
        return schains

    def get_active_schains_for_node(self, node_id: NodeId) -> List[SchainStructureWithStatus]:
        schains = []
        schain_ids = self.schains_internal.get_active_schain_ids_for_node(node_id)
        for schain_id in schain_ids:
            simple_schain = self.get(schain_id)
            schain = SchainStructureWithStatus(**asdict(simple_schain), active=True)
            schains.append(schain)
        return schains

    def name_to_id(self, name: SchainName) -> SchainHash:
        keccak_hash = keccak.new(data=name.encode('utf8'), digest_bits=256)
        return SchainHash(Web3.to_bytes(hexstr=Web3.to_hex(hexstr=HexStr(keccak_hash.hexdigest()))))

    def get_last_rotation_id(self, schain_name: SchainName) -> int:
        rotation_data = self.node_rotation.get_rotation(schain_name)
        return rotation_data.rotation_counter

    def schain_active(self, schain: SchainStructure) -> bool:
        if (
            schain.name != ''
            and schain.mainnet_owner != '0x0000000000000000000000000000000000000000'
        ):
            return True
        return False

    def get_schain_price(self, index_of_type: int, lifetime: int) -> Wei:
        return Wei(self.contract.functions.getSchainPrice(index_of_type, lifetime).call())

    @transaction_method
    def add_schain_by_foundation(
        self,
        lifetime: int,
        type_of_nodes: int,
        nonce: int,
        name: SchainName,
        options: SchainOptions | None = None,
        schain_owner: ChecksumAddress | None = None,
        schain_originator: ChecksumAddress | None = None,
    ) -> 'ContractFunction':
        if schain_owner is None:
            schain_owner = self.skale.wallet.address
        if schain_originator is None:
            schain_originator = self.skale.wallet.address
        if not options:
            options = get_default_schain_options()

        return self.contract.functions.addSchainByFoundation(
            lifetime,
            type_of_nodes,
            nonce,
            name,
            schain_owner,
            schain_originator,
            options.to_tuples(),
        )

    @transaction_method
    def grant_role(self, role: bytes, owner: ChecksumAddress) -> 'ContractFunction':
        return self.contract.functions.grantRole(role, owner)

    def schain_creator_role(self) -> bytes:
        return bytes(self.contract.functions.SCHAIN_CREATOR_ROLE().call())

    def __raw_get_options(self, schain_id: SchainHash) -> List[Any]:
        return list(self.contract.functions.getOptions(schain_id).call())

    def get_options(self, schain_id: SchainHash) -> SchainOptions:
        return parse_schain_options(raw_options=self.__raw_get_options(schain_id))

    def get_options_by_name(self, name: SchainName) -> SchainOptions:
        id_ = self.name_to_id(name)
        return self.get_options(id_)

    def restart_schain_creation(self, name: SchainName) -> 'ContractFunction':
        return self.contract.functions.restartSchainCreation(name)
