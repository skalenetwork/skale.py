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


class TimeUnit(IntEnum):
    DAY = 0
    MONTH = 1
    YEAR = 2


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
