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

from enum import IntEnum
from typing import NewType, TypedDict

from web3.types import Wei


class TimeUnit(IntEnum):
    DAY = 0
    MONTH = 1
    YEAR = 2


class BeneficiaryStatus(IntEnum):
    UNKNOWN = 0
    CONFIRMED = 1
    ACTIVE = 2
    TERMINATED = 3


PlanId = NewType('PlanId', int)


class Plan(TypedDict):
    totalVestingDuration: int
    vestingCliff: int
    vestingIntervalTimeUnit: TimeUnit
    vestingInterval: int
    isDelegationAllowed: bool
    isTerminatable: bool


class PlanWithId(Plan):
    planId: PlanId


class BeneficiaryPlan(TypedDict):
    status: BeneficiaryStatus
    statusName: str
    planId: PlanId
    startMonth: int
    fullAmount: Wei
    amountAfterLockup: Wei
