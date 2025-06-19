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
from skale.types.node import NodeId, Port


@dataclass
class NodeInfo:
    """Dataclass that represents base info about the node"""

    node_id: NodeId
    name: str
    base_port: Port

    def calc_ports(self) -> dict[str, Port]:
        return {
            'httpRpcPort': Port(self.base_port + SkaledPorts.HTTP_JSON.value),
            'httpsRpcPort': Port(self.base_port + SkaledPorts.HTTPS_JSON.value),
            'wsRpcPort': Port(self.base_port + SkaledPorts.WS_JSON.value),
            'wssRpcPort': Port(self.base_port + SkaledPorts.WSS_JSON.value),
        }

    def to_dict(self) -> dict[str, NodeId | str | Port]:
        return {
            'nodeID': self.node_id,
            'nodeName': self.name,
            'basePort': self.base_port,
            **self.calc_ports(),
        }
