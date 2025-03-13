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

    def to_tuples(self) -> list[SchainOption]:
        return [
            ('multitr', bool_to_bytes(self.multitransaction_mode)),
            ('encrypt', bool_to_bytes(self.threshold_encryption)),
            ('alloc', int_to_bytes(self.allocation_type.value)),
        ]


def parse_schain_options(raw_options: list[SchainOption]) -> SchainOptions:
    """
    Parses raw sChain options from smart contracts (list of tuples).
    Returns default values if nothing is set on contracts.
    """

    multitransaction_mode = False
    threshold_encryption = False
    allocation_type = AllocationType.DEFAULT
    if len(raw_options) > 0:
        multitransaction_mode = bytes_to_bool(raw_options[0][1])
    if len(raw_options) > 1:
        threshold_encryption = bytes_to_bool(raw_options[1][1])
    if len(raw_options) > 2:
        allocation_type = AllocationType(bytes_to_int(raw_options[2][1]))

    return SchainOptions(
        multitransaction_mode=multitransaction_mode,
        threshold_encryption=threshold_encryption,
        allocation_type=allocation_type,
    )


def get_default_schain_options() -> SchainOptions:
    return SchainOptions(
        multitransaction_mode=False,
        threshold_encryption=False,
        allocation_type=AllocationType.DEFAULT,
    )


def bool_to_bytes(bool_value: bool) -> bytes:
    return bool_value.to_bytes(1, byteorder='big')


def int_to_bytes(int_value: int) -> bytes:
    return int.to_bytes(int_value, length=1, byteorder='big')


def bytes_to_int(bytes_value: bytes) -> int:
    return int.from_bytes(bytes_value, byteorder='big')


def bytes_to_bool(bytes_value: bytes) -> bool:
    return bool(int.from_bytes(bytes_value, 'big'))
