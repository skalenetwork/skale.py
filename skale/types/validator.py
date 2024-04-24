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

from typing import NewType, TypedDict

from eth_typing import ChecksumAddress
from web3.types import Wei


ValidatorId = NewType('ValidatorId', int)


class Validator(TypedDict):
    name: str
    validator_address: ChecksumAddress
    requested_address: ChecksumAddress
    description: str
    fee_rate: int
    registration_time: int
    minimum_delegation_amount: Wei
    accept_new_requests: bool
    trusted: bool


class ValidatorWithId(Validator):
    id: ValidatorId
