#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2025-Present SKALE Labs
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

import socket
from typing import Any, List

from eth_typing import ChecksumAddress
from skale.contracts.base_contract import BaseContract
from skale.types.node import MirageNode, NodeId, Port
from skale.contracts.base_contract import transaction_method


class Nodes(BaseContract):
    def __get_raw(self, node_id: NodeId) -> List[Any]:
        return list(self.contract.functions.getNode(node_id).call())

    def get(self, node_id: NodeId) -> MirageNode:
        return self._to_node(self.__get_raw(node_id))

    def get_id(self, address: ChecksumAddress) -> NodeId:
        return self.contract.functions.getNodeId(address).call()

    def get_by_address(self, address: ChecksumAddress) -> MirageNode:
        node_id = self.get_id(address)
        return self.get(node_id)

    def get_passive_node_ids(self, node_address: ChecksumAddress) -> list[NodeId]:
        return self.contract.functions.getPassiveNodeIds(node_address).call()

    def get_active_node_ids(self) -> list[NodeId]:
        return self.contract.functions.getActiveNodesIds().call()

    def active_node_exists(self, node_id: NodeId) -> bool:
        return self.contract.functions.activeNodeExists(node_id).call()

    def _to_node(self, untyped_node: List[Any]) -> MirageNode:
        return MirageNode(
            id=untyped_node[0],
            ip=bytes(untyped_node[1]),
            ip_str=socket.inet_ntoa(untyped_node[1]),
            domain_name=untyped_node[2],
            address=ChecksumAddress(untyped_node[3]),
            port=Port(untyped_node[4]),
        )

    @transaction_method
    def register(self, ip: str, port: Port):
        ip_bytes = socket.inet_aton(ip)
        return self.contract.functions.registerNode(ip_bytes, port)

    @transaction_method
    def register_passive(self, ip: str, port: Port):
        ip_bytes = socket.inet_aton(ip)
        return self.contract.functions.registerPassiveNode(ip_bytes, port)

    @transaction_method
    def request_change_address(self, node_id: NodeId, new_address: ChecksumAddress):
        return self.contract.functions.requestChangeAddress(node_id, new_address)

    @transaction_method
    def confirm_address_change(self, node_id: NodeId):
        return self.contract.functions.confirmAddressChange(node_id)
