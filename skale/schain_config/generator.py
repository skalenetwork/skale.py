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


from skale.skale_manager import SkaleManager
from skale.types.node import NodeWithId, NodeWithSchains
from skale.types.schain import SchainName


def get_nodes_for_schain(skale: SkaleManager, name: SchainName) -> list[NodeWithId]:
    nodes = []
    ids = skale.schains_internal.get_node_ids_for_schain(name)
    for id_ in ids:
        node = skale.nodes.get(id_)
        nodes.append(NodeWithId(id=id_, **node))
    return nodes


def get_schain_nodes_with_schains(
    skale: SkaleManager, schain_name: SchainName
) -> list[NodeWithSchains]:
    """Returns list of nodes for schain with schains for all nodes"""
    nodes = get_nodes_for_schain(skale, schain_name)
    return [
        NodeWithSchains(schains=skale.schains.get_schains_for_node(node['id']), **node)
        for node in nodes
    ]
