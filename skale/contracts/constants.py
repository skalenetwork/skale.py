from skale.contracts import BaseContract
from skale.utils.constants import GAS
from skale.utils.helper import sign_and_send

class Constants(BaseContract):
    def set_periods(self, new_reward_period, new_delta_period, wallet):
        op = self.contract.functions.setPeriods(new_reward_period, new_delta_period)
        tx = sign_and_send(self.skale, op, GAS['set_periods'], wallet)
        return {'tx': tx}
