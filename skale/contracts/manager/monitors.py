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
""" Monitors.sol functions """

import socket
from web3 import Web3
from skale.contracts.base_contract import BaseContract
from skale.utils.helper import format_fields

FIELDS = ['id', 'rep_date', 'ip']


class Monitors(BaseContract):
    def __get_checked_array_raw(self, node_id):
        node_id_bytes = Web3.solidityKeccak(['uint256'], [node_id])
        return self.contract.functions.getCheckedArray(node_id_bytes).call()

    @format_fields(FIELDS, flist=True)
    def get_checked_array_struct(self, node_id):
        return self.__get_checked_array_raw(node_id)

    def get_checked_array(self, node_id):
        checked_array = self.get_checked_array_struct(node_id)
        for node in checked_array:
            node['ip'] = socket.inet_ntoa(node['ip'])
        return checked_array

    def get_last_bounty_block(self, node_index):
        return self.contract.functions.getLastBountyBlock(node_index).call()

    def get_last_received_verdict_block(self, node_index):
        return self.contract.functions.getLastReceivedVerdictBlock(node_index).call()
