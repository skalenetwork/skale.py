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
""" Get SKALE chain data """

from Crypto.Hash import keccak

from skale.contracts import BaseContract
from skale.utils.helper import format_fields


FIELDS = [
    'name', 'owner', 'indexInOwnerList', 'partOfNode', 'lifetime', 'startDate',
    'deposit', 'index', 'chainId'
]


class SChainsData(BaseContract):
    def __get_raw(self, name):
        return self.contract.functions.schains(name).call()

    @format_fields(FIELDS)
    def get(self, id_):
        res = self.__get_raw(id_)
        hash_obj = keccak.new(data=res[0].encode("utf8"), digest_bits=256)
        hash_str = "0x" + hash_obj.hexdigest()[:13]
        res.append(hash_str)
        return res

    @format_fields(FIELDS)
    def get_by_name(self, name):
        id_ = self.name_to_id(name)
        res = self.__get_raw(id_)
        hash_obj = keccak.new(data=res[0].encode("utf8"), digest_bits=256)
        hash_str = "0x" + hash_obj.hexdigest()[:13]
        res.append(hash_str)
        return res

    def get_schains_for_owner(self, account):
        schains = []
        list_size = self.get_schain_list_size(account)

        for i in range(0, list_size):
            id_ = self.get_schain_id_by_index_for_owner(account, i)
            schain = self.get(id_)
            schains.append(schain)
        return schains

    def get_schain_list_size(self, account):
        return self.contract.functions.getSchainListSize(account).call(
            {'from': account})

    def get_schain_id_by_index_for_owner(self, account, index):
        return self.contract.functions.schainIndexes(account, index).call()

    def get_node_ids_for_schain(self, name):
        id_ = self.name_to_id(name)
        return self.contract.functions.getNodesInGroup(id_).call()

    def get_schain_ids_for_node(self, node_id):
        return self.contract.functions.getSchainIdsForNode(node_id).call()

    def get_schains_for_node(self, node_id):
        schains = []
        schain_ids = self.get_schain_ids_for_node(node_id)
        for schain_id in schain_ids:
            schain = self.get(schain_id)
            schain['active'] = True if self.schain_active(schain) else False
            schains.append(schain)
        return schains

    def name_to_id(self, name):
        keccak_hash = keccak.new(data=name.encode("utf8"), digest_bits=256)
        return keccak_hash.hexdigest()

    def get_all_schains_ids(self):
        return self.contract.functions.getSchains().call()

    def get_schains_number(self):
        return self.contract.functions.numberOfSchains().call()

    def get_groups_public_key(self, group_index):
        return self.contract.functions.getGroupsPublicKey(group_index).call()

    def get_leaving_history(self, node_id):
        return self.contract.functions.getLeavingHistory(node_id).call()

    def get_rotation(self, schain_name):
        schain_id = self.name_to_id(schain_name)
        rotation_data = self.contract.functions.getRotation(schain_id).call()
        return {
            'leaving_node': rotation_data[0],
            'new_node': rotation_data[1],
            'finish_ts': rotation_data[2],
            'rotation_id': rotation_data[3]
        }

    def get_last_rotation_id(self, schain_name):
        rotation_data = self.get_rotation(schain_name)
        return rotation_data['rotation_id']

    def schain_active(self, schain):
        if schain['name'] != '' and \
                schain['owner'] != '0x0000000000000000000000000000000000000000':
            return True
