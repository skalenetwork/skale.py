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
""" Call SKALE node data example """

from skale import BlockchainEnv, Skale
from skale.utils.helper import ip_from_bytes

skale = Skale(BlockchainEnv.TEST)

nodes_ids = skale.nodes_data.get_active_node_ids()
nodes_ips = skale.nodes_data.get_active_node_ips()

ips = []
for ip in nodes_ips:
    ips.append(ip_from_bytes(ip))
print('IPS', ips)

node_data = skale.nodes_data.get(0)
print(node_data)
