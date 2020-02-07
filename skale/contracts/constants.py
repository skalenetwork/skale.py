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

from skale.contracts import BaseContract, transaction_method
from skale.transactions.tools import post_transaction
from skale.utils.constants import GAS
from skale.dataclasses.tx_res import TxRes


class Constants(BaseContract):
    @transaction_method
    def set_periods(self, new_reward_period, new_delta_period):
        op = self.contract.functions.setPeriods(new_reward_period, new_delta_period)
        tx_hash = post_transaction(self.skale.wallet, op, GAS['set_periods'])
        return TxRes(tx_hash=tx_hash)

    def get_reward_period(self):
        return self.contract.functions.rewardPeriod().call()

    def get_delta_period(self):
        return self.contract.functions.deltaPeriod().call()

    @transaction_method
    def set_check_time(self, new_check_time):
        op = self.contract.functions.setCheckTime(new_check_time)
        tx_hash = post_transaction(self.skale.wallet, op, GAS['set_check_time'])
        return TxRes(tx_hash=tx_hash)

    def get_check_time(self):
        return self.contract.functions.checkTime().call()

    @transaction_method
    def set_latency(self, new_allowable_latency):
        op = self.contract.functions.setLatency(new_allowable_latency)
        tx_hash = post_transaction(self.skale.wallet, op, GAS['set_latency'])
        return TxRes(tx_hash=tx_hash)

    def get_latency(self):
        return self.contract.functions.allowableLatency().call()

    def msr(self) -> int:
        """Minimum staking requirement to create a node.

        :returns: MSR (in wei)
        :rtype: int
        """
        return self.contract.functions.msr().call()
