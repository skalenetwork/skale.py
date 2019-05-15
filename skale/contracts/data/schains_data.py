#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" Get SKALE chain data """

from Crypto.Hash import keccak

from skale.contracts import BaseContract
from skale.utils.helper import format, ip_from_bytes, public_key_to_address
from skale.skaled_ports import SkaledPorts

from skale.dataclasses.current_node_info import CurrentNodeInfo
from skale.dataclasses.schain_node_info import SchainNodeInfo

FIELDS = [
    'name', 'owner', 'indexInOwnerList', 'partOfNode', 'lifetime', 'startDate',
    'deposit', 'index'
]

PORTS_PER_SCHAIN = 11
NUMBER_OF_PORTS = 3


class SChainsData(BaseContract):
    def __get_raw(self, name):
        return self.contract.functions.schains(name).call()

    @format(FIELDS)
    def get(self, id):
        return self.__get_raw(id)

    @format(FIELDS)
    def get_by_name(self, name):
        id = self.name_to_id(name)
        return self.__get_raw(id)

    def get_schains_for_owner(self, account):
        schains = []
        list_size = self.get_schain_list_size(account)

        for i in range(0, list_size):
            id = self.get_schain_id_by_index_for_owner(account, i)
            schain = self.get(id)
            schains.append(schain)
        return schains

    def get_schain_list_size(self, account):
        return self.contract.functions.getSchainListSize(account).call(
            {'from': account})

    def get_schain_id_by_index_for_owner(self, account, index):
        return self.contract.functions.schainIndexes(account, index).call()

    def get_current_node_for_schain_config(self, schain_name: str, node_id: int) -> CurrentNodeInfo:
        node = self.skale.nodes_data.get(node_id)
        schain_base_port = self.get_schain_base_port_on_node(schain_name, node_id, node['port'])
        return CurrentNodeInfo(
            node_name=node['name'],
            node_id=node_id,
            base_port=schain_base_port,
            bind_ip=ip_from_bytes(node['ip'])
        ).to_config()

    def get_nodes_for_schain_config(self, name):
        nodes_info = []
        nodes = self.get_nodes_for_schain(name)

        for i, node in enumerate(nodes):
            pk = node['publicKey'].hex()
            base_port = self.get_schain_base_port_on_node(name, node['id'], node['port'])

            node_info = SchainNodeInfo(
                node_name=node['name'],
                node_id=node['id'],
                base_port=base_port,

                schain_index=i,
                ip=ip_from_bytes(node['ip']),
                public_key=pk,
                public_ip=ip_from_bytes(node['publicIP']),
                owner=public_key_to_address(pk)
            ).to_config()
            nodes_info.append(node_info)
        return nodes_info

    def get_schain_base_port_on_node(self, schain_name, node_id, node_port):
        schains = self.get_schains_for_node(node_id)
        schain_index = self.get_schain_index_in_node(schain_name, schains)
        return self.calc_schain_base_port(node_port, schain_index)

    def get_schain_index_in_node(self, schain_name, node_schains):
        for index, schain in enumerate(node_schains):
            if schain_name == schain['name']:
                return index
        return -1

    def calc_schain_base_port(self, node_base_port, schain_index):
        return node_base_port + schain_index * PORTS_PER_SCHAIN

    def get_nodes_for_schain(self, name):
        nodes = []
        ids = self.get_node_ids_for_schain(name)
        for id in ids:
            node = self.skale.nodes_data.get(id)
            node['id'] = id
            nodes.append(node)
        return nodes

    def get_node_ids_for_schain(self, name):
        id = self.name_to_id(name)
        return self.contract.functions.getNodesInGroup(id).call()

    def get_schain_ids_for_node(self, node_id):
        return self.contract.functions.getSchainIdsForNode(node_id).call()

    def get_schains_for_node(self, node_id):
        schains = []
        schain_ids = self.get_schain_ids_for_node(node_id)
        for schain_id in schain_ids:
            schain = self.get(schain_id)
            schains.append(schain)
        return schains

    def name_to_id(self, name):
        keccak_hash = keccak.new(data=name.encode("utf8"), digest_bits=256)
        return keccak_hash.hexdigest()

    def get_all_schains_ids(self):
        return self.contract.functions.getSchains().call()
