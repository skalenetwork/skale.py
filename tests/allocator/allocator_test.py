"""Tests for skale/allocator/allocator.py"""

import pytest

from skale.utils.account_tools import send_eth
from skale.utils.contracts_provision import D_PLAN_ID
from skale.utils.contracts_provision.allocator import add_test_plan, connect_test_beneficiary
from skale.wallets.web3_wallet import generate_wallet

TEST_PLAN_PARAMS = {
    'totalVestingDuration': 36,
    'vestingCliff': 6,
    'vestingIntervalTimeUnit': 1,
    'vestingInterval': 6,
    'isDelegationAllowed': True,
    'isTerminatable': True,
}

D_END_TIMESTAMP = 1693526400
D_END_LOCKUP_TIMESTAMP = 1614556800


def test_is_beneficiary_registered(skale_allocator):
    wallet = generate_wallet(skale_allocator.web3)
    assert not skale_allocator.allocator.is_beneficiary_registered(wallet.address)


def test_add_plan(skale_allocator):
    plan_id = add_test_plan(skale_allocator)
    assert isinstance(plan_id, int)


def test_connect_beneficiary_to_plan(skale_allocator):
    wallet = generate_wallet(skale_allocator.web3)
    assert not skale_allocator.allocator.is_beneficiary_registered(wallet.address)
    connect_test_beneficiary(skale_allocator, D_PLAN_ID, wallet)
    assert skale_allocator.allocator.is_beneficiary_registered(wallet.address)


def test_start_vesting(skale_allocator):
    main_wallet = skale_allocator.wallet
    wallet = generate_wallet(skale_allocator.web3)

    connect_test_beneficiary(skale_allocator, D_PLAN_ID, wallet)
    send_eth(skale_allocator.web3, main_wallet, wallet.address, 0.1)

    assert skale_allocator.allocator.is_delegation_allowed(wallet.address)

    assert not skale_allocator.allocator.is_vesting_active(wallet.address)
    skale_allocator.allocator.start_vesting(wallet.address, wait_for=True)
    assert skale_allocator.allocator.is_vesting_active(wallet.address)


def test_stop_vesting(skale_allocator):
    # todo: impove test
    main_wallet = skale_allocator.wallet
    wallet = generate_wallet(skale_allocator.web3)

    connect_test_beneficiary(skale_allocator, D_PLAN_ID, wallet)
    send_eth(skale_allocator.web3, main_wallet, wallet.address, 0.1)

    assert skale_allocator.allocator.is_delegation_allowed(wallet.address)

    assert not skale_allocator.allocator.is_vesting_active(wallet.address)
    skale_allocator.allocator.start_vesting(wallet.address, wait_for=True)
    assert skale_allocator.allocator.is_vesting_active(wallet.address)

    skale_allocator.allocator.stop_vesting(wallet.address, wait_for=True)
    assert not skale_allocator.allocator.is_vesting_active(wallet.address)


def test_grant_vesting_manager_role(skale_allocator):
    wallet = generate_wallet(skale_allocator.web3)
    vesting_manager_role = skale_allocator.allocator.vesting_manager_role()
    assert not skale_allocator.allocator.has_role(vesting_manager_role, wallet.address)
    skale_allocator.allocator.grant_role(vesting_manager_role, wallet.address)
    assert skale_allocator.allocator.has_role(vesting_manager_role, wallet.address)


def test_get_beneficiary_plan_params(skale_allocator):
    wallet = generate_wallet(skale_allocator.web3)
    connect_test_beneficiary(skale_allocator, D_PLAN_ID, wallet)
    beneficiary = skale_allocator.allocator.get_beneficiary_plan_params(wallet.address)
    assert beneficiary['planId'] == 1
    assert beneficiary['startMonth'] == 8
    assert beneficiary['amountAfterLockup'] == 1000000000000000000000


def test_get_plan(skale_allocator):
    plan = skale_allocator.allocator.get_plan(D_PLAN_ID)
    assert plan == TEST_PLAN_PARAMS


def test_get_all_plans(skale_allocator):
    plans = skale_allocator.allocator.get_all_plans()
    plan_params_with_id = TEST_PLAN_PARAMS.copy()
    plan_params_with_id['planId'] = 1
    assert plan_params_with_id == plans[0]


@pytest.mark.skip('test should be updated')
def test_calculate_vested_amount(skale_allocator):
    wallet = generate_wallet(skale_allocator.web3)
    connect_test_beneficiary(skale_allocator, D_PLAN_ID, wallet)
    vested_amount = skale_allocator.allocator.calculate_vested_amount(wallet.address)
    assert vested_amount == 1000000000000000000000


def test_get_finish_vesting_time(skale_allocator):
    wallet = generate_wallet(skale_allocator.web3)
    connect_test_beneficiary(skale_allocator, D_PLAN_ID, wallet)
    res = skale_allocator.allocator.get_finish_vesting_time(wallet.address)
    assert res == D_END_TIMESTAMP


def test_get_lockup_period_end_timestamp(skale_allocator):
    wallet = generate_wallet(skale_allocator.web3)
    connect_test_beneficiary(skale_allocator, D_PLAN_ID, wallet)
    res = skale_allocator.allocator.get_lockup_period_end_timestamp(wallet.address)
    assert res == D_END_LOCKUP_TIMESTAMP


@pytest.mark.skip('test should be updated')
def test_get_time_of_next_vest(skale_allocator):
    wallet = generate_wallet(skale_allocator.web3)
    connect_test_beneficiary(skale_allocator, D_PLAN_ID, wallet)
    res = skale_allocator.allocator.get_time_of_next_vest(wallet.address)
    assert res == 1630454400
