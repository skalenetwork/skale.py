from skale.utils.web3_utils import wait_receipt

from tests.constants import NEW_REWARD_PERIOD, NEW_DELTA_PERIOD


def test_get_set_periods(skale, wallet):
    res = skale.constants.set_periods(NEW_REWARD_PERIOD, NEW_DELTA_PERIOD, wallet)
    receipt = wait_receipt(skale.web3, res['tx'])
    assert receipt['status'] == 1
    reward_period = skale.constants.get_reward_period()
    delta_period = skale.constants.get_delta_period()
    assert reward_period == NEW_REWARD_PERIOD
    assert delta_period == NEW_DELTA_PERIOD


def test_get_set_check_time(skale, wallet):
    new_check_time = 100
    res = skale.constants.set_check_time(new_check_time, wallet)
    receipt = wait_receipt(skale.web3, res['tx'])
    assert receipt['status'] == 1
    res = skale.constants.get_check_time()
    assert res == new_check_time


def test_get_set_latency(skale, wallet):
    new_latency = 1000
    res = skale.constants.set_latency(new_latency, wallet)
    receipt = wait_receipt(skale.web3, res['tx'])
    assert receipt['status'] == 1
    res = skale.constants.get_latency()
    assert res == new_latency
