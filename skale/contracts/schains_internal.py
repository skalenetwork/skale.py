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
from skale.contracts import BaseContract


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

    def get_previous_groups_public_key(self, group_index):
        return self.contract.functions.getPreviousGroupsPublicKey(group_index).call()

    def get_rotation(self, schain_name):
        schain_id = self.schains.name_to_id(schain_name)
        rotation_data = self.contract.functions.getRotation(schain_id).call()
        return {
            'leaving_node': rotation_data[0],
            'new_node': rotation_data[1],
            'finish_ts': rotation_data[2],
            'rotation_id': rotation_data[3]
        }

    def is_group_failed_dkg(self, group_index):
        return self.contract.functions.isGroupFailedDKG(group_index).call()

    def is_schain_exist(self, name):
        id_ = self.schains.name_to_id(name)
        return self.contract.functions.isSchainExist(id_).call()

    def get_groups_public_key(self, group_index):
        return self.contract.functions.getGroupsPublicKey(group_index).call()

    def get_leaving_history(self, node_id):
        raw_history = self.contract.functions.getLeavingHistory(node_id).call()
        history = [
            {
                'id': schain[0],
                'finished_rotation': schain[1]
            }
            for schain in raw_history
        ]
        return history
