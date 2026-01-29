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
    min_gas_price: HexStr | None
    max_gas_price: HexStr | None

    def to_tuples(self) -> list[SchainOption]:
        options = [
            ('multitr', bool_to_bytes(self.multitransaction_mode)),
            ('encrypt', bool_to_bytes(self.threshold_encryption)),
            ('alloc', int_to_bytes(self.allocation_type.value)),
            ('powdifficulty', hex_str_to_bytes(self.external_gas_difficulty)),
        ]
        if self.min_gas_price is not None:
            options.append(('mingasprice', hex_str_to_bytes(self.min_gas_price)))
        if self.max_gas_price is not None:
            options.append(('maxgasprice', hex_str_to_bytes(self.max_gas_price)))
        return options


def parse_schain_options(raw_options: list[SchainOption]) -> SchainOptions:
    """
    Parses raw sChain options from smart contracts (list of tuples).
    Returns default values if nothing is set on contracts.
    """
    options_map = {k: v for k, v in raw_options}
    default_options = get_default_schain_options()

    multitransaction_mode = default_options.multitransaction_mode
    if 'multitr' in options_map:
        multitransaction_mode = bytes_to_bool(options_map['multitr'])

    threshold_encryption = default_options.threshold_encryption
    if 'encrypt' in options_map:
        threshold_encryption = bytes_to_bool(options_map['encrypt'])

    allocation_type = default_options.allocation_type
    if 'alloc' in options_map:
        allocation_type = AllocationType(bytes_to_int(options_map['alloc']))

    external_gas_difficulty = default_options.external_gas_difficulty
    if 'powdifficulty' in options_map:
        external_gas_difficulty = bytes_to_hex_str(options_map['powdifficulty'])

    min_gas_price = default_options.min_gas_price
    if 'mingasprice' in options_map:
        min_gas_price = bytes_to_hex_str(options_map['mingasprice'])

    max_gas_price = default_options.max_gas_price
    if 'maxgasprice' in options_map:
        max_gas_price = bytes_to_hex_str(options_map['maxgasprice'])

    return SchainOptions(
        multitransaction_mode=multitransaction_mode,
        threshold_encryption=threshold_encryption,
        allocation_type=allocation_type,
        external_gas_difficulty=external_gas_difficulty,
        min_gas_price=min_gas_price,
        max_gas_price=max_gas_price,
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
    return int.to_bytes(int_value, length=1, byteorder='big')


def bytes_to_int(bytes_value: bytes) -> int:
    return int.from_bytes(bytes_value, byteorder='big')


def bytes_to_bool(bytes_value: bytes) -> bool:
    return bool(int.from_bytes(bytes_value, 'big'))


def hex_str_to_bytes(hex_str: HexStr) -> bytes:
    return Web3.to_bytes(hexstr=hex_str)


def bytes_to_hex_str(bytes_value: bytes) -> HexStr:
    return HexStr(Web3.to_hex(bytes_value))
