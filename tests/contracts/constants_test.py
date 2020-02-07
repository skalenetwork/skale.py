from tests.constants import NEW_REWARD_PERIOD, NEW_DELTA_PERIOD


def test_get_set_periods(skale):
    tx_res = skale.constants.set_periods(NEW_REWARD_PERIOD, NEW_DELTA_PERIOD, wait_for=True)
    assert tx_res.receipt['status'] == 1
    reward_period = skale.constants.get_reward_period()
    delta_period = skale.constants.get_delta_period()
    assert reward_period == NEW_REWARD_PERIOD
    assert delta_period == NEW_DELTA_PERIOD


def test_get_set_check_time(skale):
    new_check_time = 100
    tx_res = skale.constants.set_check_time(new_check_time, wait_for=True)
    assert tx_res.receipt['status'] == 1
    res = skale.constants.get_check_time()
    assert res == new_check_time


def test_get_set_latency(skale):
    new_latency = 1000
    tx_res = skale.constants.set_latency(new_latency, wait_for=True)
    assert tx_res.receipt['status'] == 1
    res = skale.constants.get_latency()
    assert res == new_latency
