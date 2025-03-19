#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2024-Present SKALE Labs
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
from typing import NewType

from eth_typing import ChecksumAddress
from web3.types import Wei

from skale.dataclasses.schain_options import SchainOptions


SchainName = NewType('SchainName', str)
SchainHash = NewType('SchainHash', bytes)
SchainOption = tuple[str, bytes]


@dataclass
class Schain:
    name: SchainName
    mainnet_owner: ChecksumAddress
    index_in_owner_list: int
    part_of_node: int
    lifetime: int
    start_date: int
    start_block: int
    deposit: Wei
    index: int
    generation: int
    originator: ChecksumAddress


@dataclass
class SchainStructure(Schain):
    chain_id: SchainHash
    options: SchainOptions


@dataclass
class SchainStructureWithStatus(SchainStructure):
    active: bool
