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

from enum import Enum
from typing import NewType, TypedDict

from eth_typing import ChecksumAddress
from web3.types import Wei

from skale.types.validator import ValidatorId


DelegationId = NewType('DelegationId', int)


class DelegationStatus(Enum):
    PROPOSED = 0
    ACCEPTED = 1
    CANCELED = 2
    REJECTED = 3
    DELEGATED = 4
    UNDELEGATION_REQUESTED = 5
    COMPLETED = 6


class Delegation(TypedDict):
    address: ChecksumAddress
    validator_id: ValidatorId
    amount: Wei
    delegation_period: int
    created: int
    started: int
    finished: int
    info: str


class FullDelegation(Delegation):
    id: DelegationId
    status: DelegationStatus
