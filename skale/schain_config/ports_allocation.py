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

from skale.schain_config import PORTS_PER_SCHAIN
from skale.types.node import Port
from skale.types.schain import SchainHash
from skale.utils.exceptions import SChainNotFoundException


def calc_schain_base_port(node_base_port: Port, schain_index: int) -> Port:
    return Port(node_base_port + schain_index * PORTS_PER_SCHAIN)


def get_schain_index_in_node(
    schain_hash: SchainHash, schain_hashes_on_node: list[SchainHash]
) -> int:
    try:
        return schain_hashes_on_node.index(schain_hash)
    except ValueError:
        raise SChainNotFoundException(
            f'sChain {str(schain_hash)} is not found in the list: {str(schain_hashes_on_node)}'
        )


def get_schain_base_port_on_node(
    schain_hashes_on_node: list[SchainHash], schain_hash: SchainHash, node_base_port: Port
) -> Port:
    schain_index = get_schain_index_in_node(schain_hash, schain_hashes_on_node)
    return calc_schain_base_port(node_base_port, schain_index)
