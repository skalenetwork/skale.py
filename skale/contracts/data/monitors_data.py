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
""" Get SKALE validator data """

import socket

from web3 import Web3
from skale.contracts import BaseContract


class MonitorsData(BaseContract):
    def __get_checked_array_raw(self, node_id):
        node_id_bytes = Web3.solidityKeccak(['uint256'], [node_id])
        return self.contract.functions.getCheckedArray(node_id_bytes).call()

    def get_checked_array(self, node_id):
        raw_checked_array = self.__get_checked_array_raw(node_id)
        nodes = []
        for node_in_bytes in raw_checked_array:
            node_id = int.from_bytes(node_in_bytes[:14], byteorder='big')
            report_date = int.from_bytes(node_in_bytes[14:28], byteorder='big')
            node_ip = socket.inet_ntoa(node_in_bytes[28:])
            nodes.append({'id': node_id, 'ip': node_ip,
                          'rep_date': report_date})
        return nodes

    def get_last_bounty_block(self, node_index):
        return self.contract.functions.getLastBountyBlock(node_index).call()

    def get_last_received_verdict_block(self, node_index):
        return self.contract.functions.getLastReceivedVerdictBlock(node_index).call()
