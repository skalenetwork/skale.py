from skale.contracts import BaseContract
from skale.utils.constants import GAS
from skale.utils.helper import sign_and_send


class Constants(BaseContract):
    def set_periods(self, new_reward_period, new_delta_period, wallet):
        op = self.contract.functions.setPeriods(new_reward_period, new_delta_period)
        tx = sign_and_send(self.skale, op, GAS['set_periods'], wallet)
        return {'tx': tx}

    def get_reward_period(self):
        return self.contract.functions.rewardPeriod().call()

    def get_delta_period(self):
        return self.contract.functions.deltaPeriod().call()

    def set_check_time(self, new_check_time, wallet):
        op = self.contract.functions.setCheckTime(new_check_time)
        tx = sign_and_send(self.skale, op, GAS['set_check_time'], wallet)
        return {'tx': tx}

    def get_check_time(self):
        return self.contract.functions.checkTime().call()

    def set_latency(self, new_allowable_latency, wallet):
        op = self.contract.functions.setLatency(new_allowable_latency)
        tx = sign_and_send(self.skale, op, GAS['set_latency'], wallet)
        return {'tx': tx}

    def get_latency(self):
        return self.contract.functions.allowableLatency().call()
