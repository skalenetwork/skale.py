from tests.constants import NEW_REWARD_PERIOD, NEW_DELTA_PERIOD


def test_get_set_periods(skale):
    tx_res = skale.constants_holder.set_periods(NEW_REWARD_PERIOD, NEW_DELTA_PERIOD, wait_for=True)
    assert tx_res.receipt['status'] == 1
    reward_period = skale.constants_holder.get_reward_period()
    delta_period = skale.constants_holder.get_delta_period()
    assert reward_period == NEW_REWARD_PERIOD
    assert delta_period == NEW_DELTA_PERIOD


def test_get_set_check_time(skale):
    new_check_time = 100
    tx_res = skale.constants_holder.set_check_time(new_check_time, wait_for=True)
    assert tx_res.receipt['status'] == 1
    res = skale.constants_holder.get_check_time()
    assert res == new_check_time


def test_get_set_latency(skale):
    new_latency = 1000
    tx_res = skale.constants_holder.set_latency(new_latency, wait_for=True)
    assert tx_res.receipt['status'] == 1
    res = skale.constants_holder.get_latency()
    assert res == new_latency


def get_set_launch_timestamp(skale):
    launch_ts = skale.constants_holder.get_set_launch_timestamp()
    assert launch_ts == 0
    new_launch_ts = 10000000000
    new_launch_ts = 1588600214
    skale.constants_holder.get_set_launch_timestamp(new_launch_ts, wait_for=True)
    launch_ts = skale.constants_holder.get_set_launch_timestamp()
    assert launch_ts == new_launch_ts
