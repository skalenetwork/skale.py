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

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes
from skale.utils.constants import ALLOCATOR_GAS


class Allocator(BaseContract):
    def is_beneficiary_registered(self, beneficiary_address: str) -> bool:
        """Confirms whether the beneficiary is registered in a Plan.

        :returns: Boolean value
        :rtype: bool
        """
        return self.contract.functions.isBeneficiaryRegistered(beneficiary_address).call()

    @transaction_method(gas_limit=ALLOCATOR_GAS['add_plan'])
    def add_plan(
            self,
            vesting_cliff: int,
            total_vesting_duration: int,
            vesting_step_time_unit: int,
            vesting_times: int,
            can_delegate: bool,
            is_terminatable: bool
    ) -> TxRes:
        return self.contract.functions.addPlan(vesting_cliff, total_vesting_duration,
                                               vesting_step_time_unit, vesting_times,
                                               can_delegate, is_terminatable)

    @transaction_method(gas_limit=ALLOCATOR_GAS['connect_beneficiary_to_plan'])
    def connect_beneficiary_to_plan(
            self,
            beneficiary: str,
            plan_id: int,
            start_month: int,
            full_amount: int,
            lockup_amount: int,
    ) -> TxRes:
        return self.contract.functions.connectBeneficiaryToPlan(beneficiary, plan_id, start_month,
                                                                full_amount, lockup_amount)
