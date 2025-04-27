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

from eth_typing import ChecksumAddress
from web3.contract.contract import ContractFunction

from skale.contracts.base_contract import transaction_method
from skale.contracts.skale_manager_contract import SkaleManagerContract


class ConstantsHolder(SkaleManagerContract):
    @transaction_method
    def set_periods(self, new_reward_period: int, new_delta_period: int) -> 'ContractFunction':
        return self.contract.functions.setPeriods(new_reward_period, new_delta_period)

    def get_reward_period(self) -> int:
        return int(self.contract.functions.rewardPeriod().call())

    def get_delta_period(self) -> int:
        return int(self.contract.functions.deltaPeriod().call())

    @transaction_method
    def set_check_time(self, new_check_time: int) -> 'ContractFunction':
        return self.contract.functions.setCheckTime(new_check_time)

    def get_check_time(self) -> int:
        return int(self.contract.functions.checkTime().call())

    @transaction_method
    def set_latency(self, new_allowable_latency: int) -> 'ContractFunction':
        return self.contract.functions.setLatency(new_allowable_latency)

    def get_latency(self) -> int:
        return int(self.contract.functions.allowableLatency().call())

    def get_first_delegation_month(self) -> int:
        return int(self.contract.functions.firstDelegationsMonth().call())

    def msr(self) -> int:
        """Minimum staking requirement to create a node.

        :returns: MSR (in wei)
        :rtype: int
        """
        return int(self.contract.functions.msr().call())

    @transaction_method
    def _set_msr(self, new_msr: int) -> 'ContractFunction':
        """For internal usage only"""
        return self.contract.functions.setMSR(new_msr)

    def get_launch_timestamp(self) -> int:
        return int(self.contract.functions.launchTimestamp().call())

    @transaction_method
    def set_launch_timestamp(self, launch_timestamp: int) -> 'ContractFunction':
        return self.contract.functions.setLaunchTimestamp(launch_timestamp)

    @transaction_method
    def set_rotation_delay(self, rotation_delay: int) -> 'ContractFunction':
        """For internal usage only"""
        return self.contract.functions.setRotationDelay(rotation_delay)

    def get_rotation_delay(self) -> int:
        return int(self.contract.functions.rotationDelay().call())

    def get_dkg_timeout(self) -> int:
        return int(self.contract.functions.complaintTimeLimit().call())

    @transaction_method
    def set_complaint_timelimit(self, complaint_timelimit: int) -> 'ContractFunction':
        return self.contract.functions.setComplaintTimeLimit(complaint_timelimit)

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> 'ContractFunction':
        return self.contract.functions.grantRole(role, address)

    def constants_holder_role(self) -> bytes:
        return bytes(self.contract.functions.CONSTANTS_HOLDER_MANAGER_ROLE().call())

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.hasRole(role, address).call())
