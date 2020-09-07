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

from skale.contracts.base_contract import BaseContract, transaction_method


class ConstantsHolder(BaseContract):
    @transaction_method
    def set_periods(self, new_reward_period, new_delta_period):
        return self.contract.functions.setPeriods(new_reward_period, new_delta_period)

    def get_reward_period(self):
        return self.contract.functions.rewardPeriod().call()

    def get_delta_period(self):
        return self.contract.functions.deltaPeriod().call()

    @transaction_method
    def set_check_time(self, new_check_time):
        return self.contract.functions.setCheckTime(new_check_time)

    def get_check_time(self):
        return self.contract.functions.checkTime().call()

    @transaction_method
    def set_latency(self, new_allowable_latency):
        return self.contract.functions.setLatency(new_allowable_latency)

    def get_latency(self):
        return self.contract.functions.allowableLatency().call()

    def get_first_delegation_month(self):
        return self.contract.functions.firstDelegationsMonth().call()

    def msr(self) -> int:
        """Minimum staking requirement to create a node.

        :returns: MSR (in wei)
        :rtype: int
        """
        return self.contract.functions.msr().call()

    @transaction_method
    def _set_msr(self, new_msr: int) -> None:
        """For internal usage only"""
        return self.contract.functions.setMSR(new_msr)

    def get_launch_timestamp(self) -> int:
        return self.contract.functions.launchTimestamp().call()

    @transaction_method
    def set_launch_timestamp(self, launch_timestamp: int):
        return self.contract.functions.setLaunchTimestamp(launch_timestamp)

    @transaction_method
    def set_rotation_delay(self, rotation_delay: int) -> None:
        """For internal usage only"""
        return self.contract.functions.setRotationDelay(rotation_delay)

    def get_rotation_delay(self) -> int:
        return self.contract.functions.rotationDelay().call()
