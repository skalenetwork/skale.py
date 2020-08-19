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


def get_nodes_for_schain(skale, name):
    nodes = []
    ids = skale.schains_internal.get_node_ids_for_schain(name)
    for id_ in ids:
        node = skale.nodes.get(id_)
        node['id'] = id_
        nodes.append(node)
    return nodes


def get_schain_nodes_with_schains(skale, schain_name) -> list:
    """Returns list of nodes for schain with schains for all nodes"""
    nodes = get_nodes_for_schain(skale, schain_name)
    for node in nodes:
        group_index = skale.web3.sha3(text=schain_name)
        node['schains'] = skale.schains.get_schains_for_node(node['id'])
        node['bls_public_key'] = skale.key_storage.get_bls_public_key(group_index, node['id'])
    return nodes
