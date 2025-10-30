import random

import pytest

from skale.transactions.result import DryRunRevertError
from tests.constants import NEW_DELTA_PERIOD, NEW_REWARD_PERIOD


def test_get_set_periods(skale):
    skale.constants_holder.set_check_time(10, wait_for=True)
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


def test_get_set_launch_timestamp(skale):
    launch_ts = skale.constants_holder.get_launch_timestamp()
    assert isinstance(launch_ts, int)
    with pytest.raises(DryRunRevertError):
        skale.constants_holder.set_launch_timestamp(launch_ts, wait_for=True)


def test_get_set_rotation_delay(skale):
    rotation_delay = skale.constants_holder.get_rotation_delay()
    assert isinstance(rotation_delay, int) and rotation_delay > 0
    new_rotation_delay = 1000
    skale.constants_holder.set_rotation_delay(new_rotation_delay, wait_for=True)
    rotation_delay = skale.constants_holder.get_rotation_delay()
    assert rotation_delay == new_rotation_delay


def test_get_first_delegation_month(skale):
    fdm = skale.constants_holder.get_first_delegation_month()
    assert fdm == 0


def test_get_set_complaint_timelimit(skale):
    new_dkg_timeout = random.randint(100, 100000)
    dkg_timeout_before = skale.constants_holder.get_dkg_timeout()
    skale.constants_holder.set_complaint_timelimit(new_dkg_timeout, wait_for=True)
    dkg_timeout_after = skale.constants_holder.get_dkg_timeout()
    assert dkg_timeout_after != dkg_timeout_before
    assert dkg_timeout_after == new_dkg_timeout
