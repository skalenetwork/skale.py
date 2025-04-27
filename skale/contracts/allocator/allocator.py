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
"""SKALE Allocator Core Escrow methods"""

from typing import Any, Dict, List

from eth_typing import ChecksumAddress
from web3 import Web3
from web3.contract.contract import ContractFunction
from web3.exceptions import ContractLogicError
from web3.types import Wei

from skale.contracts.allocator_contract import AllocatorContract
from skale.contracts.base_contract import transaction_method
from skale.types.allocation import (
    BeneficiaryStatus,
    BeneficiaryPlan,
    Plan,
    PlanId,
    PlanWithId,
    TimeUnit,
)
from skale.utils.helper import format_fields


PLAN_FIELDS = [
    'totalVestingDuration',
    'vestingCliff',
    'vestingIntervalTimeUnit',
    'vestingInterval',
    'isDelegationAllowed',
    'isTerminatable',
]

BENEFICIARY_FIELDS = ['status', 'planId', 'startMonth', 'fullAmount', 'amountAfterLockup']

MAX_NUM_OF_PLANS = 9999
MAX_NUM_OF_BENEFICIARIES = 9999


class Allocator(AllocatorContract):
    def is_beneficiary_registered(self, beneficiary_address: ChecksumAddress) -> bool:
        """Confirms whether the beneficiary is registered in a Plan.

        :returns: Boolean value
        :rtype: bool
        """
        return bool(self.contract.functions.isBeneficiaryRegistered(beneficiary_address).call())

    def is_delegation_allowed(self, beneficiary_address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.isDelegationAllowed(beneficiary_address).call())

    def is_vesting_active(self, beneficiary_address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.isVestingActive(beneficiary_address).call())

    def get_escrow_address(self, beneficiary_address: ChecksumAddress) -> ChecksumAddress:
        return Web3.to_checksum_address(
            self.contract.functions.getEscrowAddress(beneficiary_address).call()
        )

    @transaction_method
    def add_plan(
        self,
        vesting_cliff: int,
        total_vesting_duration: int,
        vesting_interval_time_unit: TimeUnit,
        vesting_interval: int,
        can_delegate: bool,
        is_terminatable: bool,
    ) -> 'ContractFunction':
        return self.contract.functions.addPlan(
            vestingCliff=vesting_cliff,
            totalVestingDuration=total_vesting_duration,
            vestingIntervalTimeUnit=vesting_interval_time_unit.value,
            vestingInterval=vesting_interval,
            canDelegate=can_delegate,
            isTerminatable=is_terminatable,
        )

    @transaction_method
    def connect_beneficiary_to_plan(
        self,
        beneficiary_address: ChecksumAddress,
        plan_id: int,
        start_month: int,
        full_amount: int,
        lockup_amount: int,
    ) -> 'ContractFunction':
        return self.contract.functions.connectBeneficiaryToPlan(
            beneficiary=beneficiary_address,
            planId=plan_id,
            startMonth=start_month,
            fullAmount=full_amount,
            lockupAmount=lockup_amount,
        )

    @transaction_method
    def start_vesting(self, beneficiary_address: ChecksumAddress) -> 'ContractFunction':
        return self.contract.functions.startVesting(beneficiary_address)

    @transaction_method
    def stop_vesting(self, beneficiary_address: ChecksumAddress) -> 'ContractFunction':
        return self.contract.functions.stopVesting(beneficiary_address)

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> 'ContractFunction':
        return self.contract.functions.grantRole(role, address)

    def vesting_manager_role(self) -> bytes:
        return bytes(self.contract.functions.VESTING_MANAGER_ROLE().call())

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.hasRole(role, address).call())

    def __get_beneficiary_plan_params_raw(self, beneficiary_address: ChecksumAddress) -> List[Any]:
        return list(self.contract.functions.getBeneficiaryPlanParams(beneficiary_address).call())

    @format_fields(BENEFICIARY_FIELDS)
    def get_beneficiary_plan_params_dict(self, beneficiary_address: ChecksumAddress) -> List[Any]:
        return self.__get_beneficiary_plan_params_raw(beneficiary_address)

    def get_beneficiary_plan_params(self, beneficiary_address: ChecksumAddress) -> BeneficiaryPlan:
        plan_params = self.get_beneficiary_plan_params_dict(beneficiary_address)
        if plan_params is None:
            raise ValueError('Plan for ', beneficiary_address, ' is missing')
        if isinstance(plan_params, list):
            return self._to_beneficiary_plan(
                {**plan_params[0], 'statusName': BeneficiaryStatus(plan_params[0]['status']).name}
            )
        if isinstance(plan_params, dict):
            return self._to_beneficiary_plan(
                {**plan_params, 'statusName': BeneficiaryStatus(plan_params.get('status', 0)).name}
            )
        raise TypeError(f'Internal error on getting plan params for ${beneficiary_address}')

    def __get_plan_raw(self, plan_id: PlanId) -> List[Any]:
        return list(self.contract.functions.getPlan(plan_id).call())

    @format_fields(PLAN_FIELDS)
    def get_untyped_plan(self, plan_id: PlanId) -> List[Any]:
        return self.__get_plan_raw(plan_id)

    def get_plan(self, plan_id: PlanId) -> Plan:
        untyped_plan = self.get_untyped_plan(plan_id)
        if untyped_plan is None:
            raise ValueError('Plan ', plan_id, ' is missing')
        if isinstance(untyped_plan, list):
            return self._to_plan(untyped_plan[0])
        if isinstance(untyped_plan, dict):
            return self._to_plan(untyped_plan)
        raise TypeError(plan_id)

    def get_all_plans(self) -> List[PlanWithId]:
        plans = []
        for i in range(1, MAX_NUM_OF_PLANS):
            try:
                plan_id = PlanId(i)
                plan = PlanWithId({**self.get_plan(plan_id), 'planId': plan_id})
                plans.append(plan)
            except (ContractLogicError, ValueError):
                break
        return plans

    def calculate_vested_amount(self, address: ChecksumAddress) -> Wei:
        return Wei(self.contract.functions.calculateVestedAmount(address).call())

    def get_finish_vesting_time(self, address: ChecksumAddress) -> int:
        return int(self.contract.functions.getFinishVestingTime(address).call())

    def get_lockup_period_end_timestamp(self, address: ChecksumAddress) -> int:
        return int(self.contract.functions.getLockupPeriodEndTimestamp(address).call())

    def get_time_of_next_vest(self, address: ChecksumAddress) -> int:
        return int(self.contract.functions.getTimeOfNextVest(address).call())

    def _to_plan(self, untyped_plan: Dict[str, Any]) -> Plan:
        return Plan(
            {
                'totalVestingDuration': int(untyped_plan['totalVestingDuration']),
                'vestingCliff': int(untyped_plan['vestingCliff']),
                'vestingIntervalTimeUnit': TimeUnit(untyped_plan['vestingIntervalTimeUnit']),
                'vestingInterval': int(untyped_plan['vestingInterval']),
                'isDelegationAllowed': bool(untyped_plan['isDelegationAllowed']),
                'isTerminatable': bool(untyped_plan['isTerminatable']),
            }
        )

    def _to_beneficiary_plan(self, untyped_beneficiary_plan: Dict[str, Any]) -> BeneficiaryPlan:
        return BeneficiaryPlan(
            {
                'status': BeneficiaryStatus(untyped_beneficiary_plan['status']),
                'statusName': str(untyped_beneficiary_plan['statusName']),
                'planId': PlanId(untyped_beneficiary_plan['planId']),
                'startMonth': int(untyped_beneficiary_plan['startMonth']),
                'fullAmount': Wei(untyped_beneficiary_plan['fullAmount']),
                'amountAfterLockup': Wei(untyped_beneficiary_plan['amountAfterLockup']),
            }
        )
