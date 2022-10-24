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
""" Schains.sol functions """

import functools
from dataclasses import dataclass, asdict

from Crypto.Hash import keccak

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes
from skale.utils.helper import format_fields
from skale.dataclasses.schain_options import (
    SchainOptions, get_default_schain_options, parse_schain_options
)


FIELDS = [
    'name', 'mainnetOwner', 'indexInOwnerList', 'partOfNode', 'lifetime', 'startDate', 'startBlock',
    'deposit', 'index', 'generation', 'originator', 'chainId', 'multitransactionMode',
    'thresholdEncryption'
]


@dataclass
class SchainStructure:
    name: str
    mainnet_owner: str
    index_in_owner_list: int
    part_of_node: int
    lifetime: int
    start_date: int
    start_block: int
    deposit: int
    index: int
    generation: int
    originator: str
    chain_id: int
    options: SchainOptions


class SChains(BaseContract):
    """Wrapper for some of the Schains.sol functions"""

    def name_to_group_id(self, name):
        return self.skale.web3.keccak(text=name)

    @property
    @functools.lru_cache()
    def schains_internal(self):
        return self.skale.schains_internal

    @property
    @functools.lru_cache()
    def node_rotation(self):
        return self.skale.node_rotation

    @format_fields(FIELDS)
    def get(self, id_, obj=False):
        res = self.schains_internal.get_raw(id_)
        hash_obj = keccak.new(data=res[0].encode("utf8"), digest_bits=256)
        hash_str = "0x" + hash_obj.hexdigest()[:13]
        res.append(hash_str)
        options = self.get_options(id_)
        if obj:  # TODO: temporary solution for backwards compatibility
            return SchainStructure(*res, options=options)
        else:
            res += asdict(options).values()
        return res

    @format_fields(FIELDS)
    def get_by_name(self, name, obj=False):
        id_ = self.name_to_id(name)
        return self.get(id_, obj=obj)

    def get_schains_for_owner(self, account):
        schains = []
        list_size = self.schains_internal.get_schain_list_size(account)

        for i in range(0, list_size):
            id_ = self.schains_internal.get_schain_id_by_index_for_owner(account, i)
            schain = self.get(id_)
            schains.append(schain)
        return schains

    def get_schains_for_node(self, node_id):
        schains = []
        schain_ids = self.schains_internal.get_schain_ids_for_node(node_id)
        for schain_id in schain_ids:
            schain = self.get(schain_id)
            schain['active'] = True if self.schain_active(schain) else False
            schains.append(schain)
        return schains

    def get_active_schains_for_node(self, node_id):
        schains = []
        schain_ids = self.schains_internal.get_active_schain_ids_for_node(node_id)
        for schain_id in schain_ids:
            schain = self.get(schain_id)
            schain['active'] = True
            schains.append(schain)
        return schains

    def name_to_id(self, name):
        keccak_hash = keccak.new(data=name.encode("utf8"), digest_bits=256)
        return '0x' + keccak_hash.hexdigest()

    def get_last_rotation_id(self, schain_name):
        rotation_data = self.node_rotation.get_rotation(schain_name)
        return rotation_data['rotation_id']

    def schain_active(self, schain):
        if schain['name'] != '' and \
                schain['mainnetOwner'] != '0x0000000000000000000000000000000000000000':
            return True

    def get_schain_price(self, index_of_type, lifetime):
        return self.contract.functions.getSchainPrice(index_of_type,
                                                      lifetime).call()

    @transaction_method
    def add_schain_by_foundation(
        self,
        lifetime: int,
        type_of_nodes: int,
        nonce: int,
        name: str,
        options: SchainOptions = None,
        schain_owner=None,
        schain_originator=None
    ) -> TxRes:
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
            options.to_tuples()
        )

    @transaction_method
    def grant_role(self, role: bytes, owner: str) -> TxRes:
        return self.contract.functions.grantRole(role, owner)

    def schain_creator_role(self):
        return self.contract.functions.SCHAIN_CREATOR_ROLE().call()

    def __raw_get_options(self, schain_id: str) -> list:
        return self.contract.functions.getOptions(schain_id).call()

    def get_options(self, schain_id: str) -> SchainOptions:
        return parse_schain_options(
            raw_options=self.__raw_get_options(schain_id)
        )

    def get_options_by_name(self, name: str) -> SchainOptions:
        id_ = self.name_to_id(name)
        return self.get_options(id_)
