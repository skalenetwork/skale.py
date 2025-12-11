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
from typing import Any, NewType

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

    def to_dict(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'mainnet_owner': self.mainnet_owner,
            'index_in_owner_list': self.index_in_owner_list,
            'part_of_node': self.part_of_node,
            'lifetime': self.lifetime,
            'start_date': self.start_date,
            'start_block': self.start_block,
            'deposit': int(self.deposit),
            'index': self.index,
            'generation': self.generation,
            'originator': self.originator,
        }


@dataclass
class SchainStructure(Schain):
    schain_hash: SchainHash
    options: SchainOptions
    active: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            **super().to_dict(),
            'schain_hash': self.schain_hash.hex(),
            'options': {
                'multitransaction_mode': self.options.multitransaction_mode,
                'threshold_encryption': self.options.threshold_encryption,
                'allocation_type': self.options.allocation_type.value,
            },
            'active': self.active,
        }
