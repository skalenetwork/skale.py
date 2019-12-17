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

from skale.dataclasses.skaled_ports import SkaledPorts


class NodeInfo():
    def __init__(self, node_id, node_name, base_port):
        self.node_id = node_id
        self.node_name = node_name
        self.base_port = base_port
        self.calc_ports()

    def calc_ports(self):
        self.http_rpc_port = self.base_port + SkaledPorts.HTTP_JSON.value
        self.https_rpc_port = self.base_port + SkaledPorts.HTTPS_JSON.value
        self.ws_rpc_port = self.base_port + SkaledPorts.WS_JSON.value
        self.wss_rpc_port = self.base_port + SkaledPorts.WSS_JSON.value

    def to_config(self):
        return {
            'nodeID': self.node_id,
            'nodeName': self.node_name,
            'basePort': self.base_port,
            'httpRpcPort': self.http_rpc_port,
            'httpsRpcPort': self.https_rpc_port,
            'wsRpcPort': self.ws_rpc_port,
            'wssRpcPort': self.wss_rpc_port
        }
