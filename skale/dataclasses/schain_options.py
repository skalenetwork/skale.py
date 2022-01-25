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

from dataclasses import dataclass


@dataclass
class SchainOptions:
    multitransaction_mode: bool
    threshold_encryption: bool

    def to_tuples(self) -> list:
        return [
            ('multitr', bool_to_bytes(self.multitransaction_mode)),
            ('encrypt', bool_to_bytes(self.threshold_encryption))
        ]


def parse_schain_options(raw_options: list) -> SchainOptions:
    """
    Parses raw sChain options from smart contracts (list of tuples).
    Returns default values if nothing is set on contracts.
    """
    if len(raw_options) == 0:
        return get_default_schain_options()
    return SchainOptions(
        multitransaction_mode=bytes_to_bool(raw_options[0][1]),
        threshold_encryption=bytes_to_bool(raw_options[1][1])
    )


def get_default_schain_options() -> SchainOptions:
    return SchainOptions(
        multitransaction_mode=False,
        threshold_encryption=False
    )


def bool_to_bytes(bool_value: bool) -> bytes:
    return bool_value.to_bytes(1, byteorder='big')


def bytes_to_bool(bytes_value: bytes) -> bool:
    return bool(int.from_bytes(bytes_value, 'big'))
