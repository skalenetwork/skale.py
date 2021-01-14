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

from dataclasses import dataclass
from skale.dataclasses.skaled_ports import SkaledPorts


@dataclass
class NodeInfo():
    """Dataclass that represents base info about the node"""
    node_id: int
    name: str
    base_port: int

    def calc_ports(self):
        return {
            'httpRpcPort': self.base_port + SkaledPorts.HTTP_JSON.value,
            'httpsRpcPort': self.base_port + SkaledPorts.HTTPS_JSON.value,
            'wsRpcPort': self.base_port + SkaledPorts.WS_JSON.value,
            'wssRpcPort': self.base_port + SkaledPorts.WSS_JSON.value,
            'infoHttpRpcPort': self.base_port + SkaledPorts.INFO_HTTP_JSON.value
        }

    def to_dict(self):
        return {
            'nodeID': self.node_id,
            'nodeName': self.name,
            'basePort': self.base_port,
            **self.calc_ports()
        }
