#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" SKALE chain data example """

import json

from skale import BlockchainEnv, Skale
from skale.utils.helper import ip_from_bytes

skale = Skale(BlockchainEnv.DO)

# todo: get all nodes
node_idx = skale.nodes_data.get_active_node_ids()

print(node_idx)

schains = []
sizes = []

for node_index in node_idx:

    node = skale.nodes_data.get(node_index)

    node_struct = {
        'name': node['name'],
        'ip': ip_from_bytes(node['ip']),
        'basePort': node['port'],
        'publicIP': ip_from_bytes(node['publicIP']),
    }

    schains_for_node = skale.schains_data.get_schains_for_node(node_index)
    schains.append({
        'schains': schains_for_node,
        'amount': len(schains_for_node),
        'node': node_struct
    })
    sizes.append(len(schains_for_node))


with open('data.json', 'w') as outfile:
    json.dump(schains, outfile)


print(schains)
print(sizes)

# group and print!
