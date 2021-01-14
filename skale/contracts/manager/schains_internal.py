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
""" SchainsInternal.sol functions """

import functools
from skale.contracts.base_contract import BaseContract


class SChainsInternal(BaseContract):
    """Wrapper for some of the SchainsInternal.sol functions"""

    @property
    @functools.lru_cache()
    def schains(self):
        return self.skale.get_contract_by_name('schains')

    def get_raw(self, name):
        return self.contract.functions.schains(name).call()

    def get_all_schains_ids(self):
        return self.contract.functions.getSchains().call()

    def get_schains_number(self):
        return self.contract.functions.numberOfSchains().call()

    def get_schain_list_size(self, account):
        return self.contract.functions.getSchainListSize(account).call(
            {'from': account})

    def get_schain_id_by_index_for_owner(self, account, index):
        return self.contract.functions.schainIndexes(account, index).call()

    def get_node_ids_for_schain(self, name):
        id_ = self.schains.name_to_id(name)
        return self.contract.functions.getNodesInGroup(id_).call()

    def get_schain_ids_for_node(self, node_id):
        return self.contract.functions.getSchainIdsForNode(node_id).call()

    def is_schain_exist(self, name):
        id_ = self.schains.name_to_id(name)
        return self.contract.functions.isSchainExist(id_).call()

    def get_active_schain_ids_for_node(self, node_id):
        return self.contract.functions.getActiveSchains(node_id).call()
