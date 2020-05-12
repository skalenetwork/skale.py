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
""" Get SKALE node data """

import socket

from Crypto.Hash import keccak
from web3.exceptions import BadFunctionCallOutput

from skale.contracts import BaseContract
from skale.utils.helper import format_fields

FIELDS = [
    'name', 'ip', 'publicIP', 'port', 'publicKey', 'start_block',
    'last_reward_date', 'finish_time', 'status', 'validator_id'
]

COMPACT_FIELDS = ['schainIndex', 'nodeID', 'ip', 'basePort']
SCHAIN_CONFIG_FIELDS = [
    'schainIndex', 'nodeID', 'nodeName', 'ip', 'basePort',
    'publicKey', 'publicIP', 'owner',
    'httpRpcPort', 'httpsRpcPort', 'wsRpcPort', 'wssRpcPort'
]


class Nodes(BaseContract):
    def __get_raw(self, node_id):
        try:
            return self.contract.functions.nodes(node_id).call()
        except (ValueError, BadFunctionCallOutput):
            return None

    @format_fields(FIELDS)
    def get(self, node_id):
        return self.__get_raw(node_id)

    @format_fields(FIELDS)
    def get_by_name(self, name):
        name_hash = self.name_to_id(name)
        id = self.contract.functions.nodesNameToIndex(name_hash).call()
        return self.__get_raw(id)

    def get_active_node_ids(self):
        return self.contract.functions.getActiveNodeIds().call()

    def get_active_node_ips(self):
        return self.contract.functions.getActiveNodeIPs().call()

    def get_active_node_ids_by_address(self, account):
        return self.contract.functions.getActiveNodesByAddress().call(
            {'from': account})

    def name_to_id(self, name):
        keccak_hash = keccak.new(data=name.encode("utf8"), digest_bits=256)
        return keccak_hash.hexdigest()

    def is_node_name_available(self, name):
        node_id = self.name_to_id(name)
        return not self.contract.functions.nodesNameCheck(node_id).call()

    def is_node_ip_available(self, ip):
        ip_bytes = socket.inet_aton(ip)
        return not self.contract.functions.nodesIPCheck(ip_bytes).call()

    def node_name_to_index(self, name):
        name_hash = self.name_to_id(name)
        return self.contract.functions.nodesNameToIndex(name_hash).call()

    def get_node_status(self, node_id):
        return self.contract.functions.getNodeStatus(node_id).call()

    def get_node_finish_time(self, node_id):
        return self.contract.functions.getNodeFinishTime(node_id).call()
