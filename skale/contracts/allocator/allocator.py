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
""" SKALE Allocator Core Escrow methods """

from enum import IntEnum

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes
from skale.utils.helper import format_fields


PLAN_FIELDS = [
    'totalVestingDuration',
    'vestingCliff',
    'vestingIntervalTimeUnit',
    'vestingInterval',
    'isDelegationAllowed',
    'isTerminatable'
]

BENEFICIARY_FIELDS = [
    'status',
    'planId',
    'startMonth',
    'fullAmount',
    'amountAfterLockup'
]

MAX_NUM_OF_PLANS = 9999
MAX_NUM_OF_BENEFICIARIES = 9999


class TimeUnit(IntEnum):
    DAY = 0
    MONTH = 1
    YEAR = 2


class BeneficiaryStatus(IntEnum):
    UNKNOWN = 0
    CONFIRMED = 1
    ACTIVE = 2
    TERMINATED = 3


class Allocator(BaseContract):
    def is_beneficiary_registered(self, beneficiary_address: str) -> bool:
        """Confirms whether the beneficiary is registered in a Plan.

        :returns: Boolean value
        :rtype: bool
        """
        return self.contract.functions.isBeneficiaryRegistered(beneficiary_address).call()

    def is_delegation_allowed(self, beneficiary_address: str) -> bool:
        return self.contract.functions.isDelegationAllowed(beneficiary_address).call()

    def is_vesting_active(self, beneficiary_address: str) -> bool:
        return self.contract.functions.isVestingActive(beneficiary_address).call()

    def get_escrow_address(self, beneficiary_address: str) -> str:
        return self.contract.functions.getEscrowAddress(beneficiary_address).call()

    @transaction_method
    def add_plan(
            self,
            vesting_cliff: int,
            total_vesting_duration: int,
            vesting_interval_time_unit: TimeUnit,
            vesting_interval: int,
            can_delegate: bool,
            is_terminatable: bool
    ) -> TxRes:
        return self.contract.functions.addPlan(
            vestingCliff=vesting_cliff,
            totalVestingDuration=total_vesting_duration,
            vestingIntervalTimeUnit=vesting_interval_time_unit.value,
            vestingInterval=vesting_interval,
            canDelegate=can_delegate,
            isTerminatable=is_terminatable
        )

    @transaction_method
    def connect_beneficiary_to_plan(
            self,
            beneficiary_address: str,
            plan_id: int,
            start_month: int,
            full_amount: int,
            lockup_amount: int,
    ) -> TxRes:
        return self.contract.functions.connectBeneficiaryToPlan(
            beneficiary=beneficiary_address,
            planId=plan_id,
            startMonth=start_month,
            fullAmount=full_amount,
            lockupAmount=lockup_amount
        )

    @transaction_method
    def start_vesting(self, beneficiary_address: str) -> TxRes:
        return self.contract.functions.startVesting(beneficiary_address)

    @transaction_method
    def stop_vesting(self, beneficiary_address: str) -> TxRes:
        return self.contract.functions.stopVesting(beneficiary_address)

    @transaction_method
    def grant_role(self, role: bytes, address: str) -> TxRes:
        return self.contract.functions.grantRole(role, address)

    def vesting_manager_role(self) -> bytes:
        return self.contract.functions.VESTING_MANAGER_ROLE().call()

    def has_role(self, role: bytes, address: str) -> bool:
        return self.contract.functions.hasRole(role, address).call()

    def __get_beneficiary_plan_params_raw(self, beneficiary_address: str):
        return self.contract.functions.getBeneficiaryPlanParams(beneficiary_address).call()

    @format_fields(BENEFICIARY_FIELDS)
    def get_beneficiary_plan_params_dict(self, beneficiary_address: str) -> dict:
        return self.__get_beneficiary_plan_params_raw(beneficiary_address)

    def get_beneficiary_plan_params(self, beneficiary_address: str) -> dict:
        plan_params = self.get_beneficiary_plan_params_dict(beneficiary_address)
        plan_params['statusName'] = BeneficiaryStatus(plan_params['status']).name
        return plan_params

    def __get_plan_raw(self, plan_id: int):
        return self.contract.functions.getPlan(plan_id).call()

    @format_fields(PLAN_FIELDS)
    def get_plan(self, plan_id: int) -> dict:
        return self.__get_plan_raw(plan_id)

    def get_all_plans(self) -> dict:
        plans = []
        for i in range(1, MAX_NUM_OF_PLANS):
            try:
                plan = self.get_plan(i)
                plan['planId'] = i
                plans.append(plan)
            except ValueError:
                break
        return plans

    def calculate_vested_amount(self, address: str) -> int:
        return self.contract.functions.calculateVestedAmount(address).call()

    def get_finish_vesting_time(self, address: str) -> int:
        return self.contract.functions.getFinishVestingTime(address).call()

    def get_lockup_period_end_timestamp(self, address: str) -> int:
        return self.contract.functions.getLockupPeriodEndTimestamp(address).call()

    def get_time_of_next_vest(self, address: str) -> int:
        return self.contract.functions.getTimeOfNextVest(address).call()
