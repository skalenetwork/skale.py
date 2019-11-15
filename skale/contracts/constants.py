from skale.contracts import BaseContract
from skale.transactions.tools import post_transaction
from skale.utils.constants import GAS


class Constants(BaseContract):
    def set_periods(self, new_reward_period, new_delta_period):
        op = self.contract.functions.setPeriods(new_reward_period, new_delta_period)
        tx = post_transaction(self.skale.wallet, op, GAS['set_periods'])
        return {'tx': tx}

    def get_reward_period(self):
        return self.contract.functions.rewardPeriod().call()

    def get_delta_period(self):
        return self.contract.functions.deltaPeriod().call()

    def set_check_time(self, new_check_time):
        op = self.contract.functions.setCheckTime(new_check_time)
        tx = post_transaction(self.skale.wallet, op, GAS['set_check_time'])
        return {'tx': tx}

    def get_check_time(self):
        return self.contract.functions.checkTime().call()

    def set_latency(self, new_allowable_latency):
        op = self.contract.functions.setLatency(new_allowable_latency)
        tx = post_transaction(self.skale.wallet, op, GAS['set_latency'])
        return {'tx': tx}

    def get_latency(self):
        return self.contract.functions.allowableLatency().call()
