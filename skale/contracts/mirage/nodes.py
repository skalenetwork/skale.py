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

from typing import Any, List

from eth_typing import ChecksumAddress
from skale.contracts.base_contract import BaseContract
from skale.types.node import MirageNode, NodeId, Port


class Nodes(BaseContract):
    def __get_raw(self, node_id: NodeId) -> List[Any]:
        return list(self.contract.functions.nodes(node_id).call())

    def get(self, node_id: NodeId) -> MirageNode:
        return self._to_node(self.__get_raw(node_id))

    def _to_node(self, untyped_node: List[Any]) -> MirageNode:
        return MirageNode(
            {
                'id': untyped_node[0],
                'ip': bytes(untyped_node[1]),
                'domain_name': untyped_node[2],
                'address': ChecksumAddress(untyped_node[3]),
                'port': Port(untyped_node[4]),
            }
        )
