#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2021 SKALE Labs
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
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skale.types.schain import SchainOption
from enum import Enum

from eth_typing import HexStr
from web3 import Web3


class AllocationType(int, Enum):
    DEFAULT = 0
    NO_FILESTORAGE = 1
    MAX_CONTRACT_STORAGE = 2
    MAX_CONSENSUS_DB = 3
    MAX_FILESTORAGE = 4


@dataclass
class SchainOptions:
    multitransaction_mode: bool
    threshold_encryption: bool
    allocation_type: AllocationType
    external_gas_difficulty: HexStr
    min_gas_price: int | None
    max_gas_price: int | None

    def to_tuples(self) -> list[SchainOption]:
        options = [
            ('multitr', bool_to_bytes(self.multitransaction_mode)),
            ('encrypt', bool_to_bytes(self.threshold_encryption)),
            ('alloc', int_to_bytes(self.allocation_type.value)),
            ('powdifficulty', hex_str_to_bytes(self.external_gas_difficulty)),
        ]
        if self.min_gas_price is not None:
            options.append(('mingasprice', int_to_bytes(self.min_gas_price)))
        if self.max_gas_price is not None:
            options.append(('maxgasprice', int_to_bytes(self.max_gas_price)))
        return options


def parse_schain_options(raw_options: list[SchainOption]) -> SchainOptions:
    """
    Parses raw sChain options from smart contracts (list of tuples).
    Returns default values if nothing is set on contracts.
    """
    options_map = {k: v for k, v in raw_options}
    default_options = get_default_schain_options()

    def get_val(key, converter, default):
        return converter(options_map[key]) if key in options_map else default

    return SchainOptions(
        multitransaction_mode=get_val(
            'multitr', bytes_to_bool, default_options.multitransaction_mode
        ),
        threshold_encryption=get_val(
            'encrypt', bytes_to_bool, default_options.threshold_encryption
        ),
        allocation_type=get_val(
            'alloc',
            lambda x: AllocationType(bytes_to_int(x)),
            default_options.allocation_type,
        ),
        external_gas_difficulty=get_val(
            'powdifficulty', bytes_to_hex_str, default_options.external_gas_difficulty
        ),
        min_gas_price=get_val('mingasprice', bytes_to_int, default_options.min_gas_price),
        max_gas_price=get_val('maxgasprice', bytes_to_int, default_options.max_gas_price),
    )


def get_default_schain_options() -> SchainOptions:
    return SchainOptions(
        multitransaction_mode=False,
        threshold_encryption=False,
        allocation_type=AllocationType.DEFAULT,
        external_gas_difficulty=HexStr('0x01'),
        min_gas_price=None,
        max_gas_price=None,
    )


def bool_to_bytes(bool_value: bool) -> bytes:
    return bool_value.to_bytes(1, byteorder='big')


def int_to_bytes(int_value: int) -> bytes:
    return int_value.to_bytes(max(1, (int_value.bit_length() + 7) // 8), byteorder='big')


def bytes_to_int(bytes_value: bytes) -> int:
    return int.from_bytes(bytes_value, byteorder='big')


def bytes_to_bool(bytes_value: bytes) -> bool:
    return bool(int.from_bytes(bytes_value, 'big'))


def hex_str_to_bytes(hex_str: HexStr) -> bytes:
    return Web3.to_bytes(hexstr=hex_str)


def bytes_to_hex_str(bytes_value: bytes) -> HexStr:
    return Web3.to_hex(bytes_value)
