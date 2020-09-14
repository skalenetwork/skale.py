""" Tests for skale/allocator/allocator.py """

from skale.wallets.web3_wallet import generate_wallet
from skale.utils.account_tools import send_ether

from skale.utils.contracts_provision import D_PLAN_ID
from skale.utils.contracts_provision.allocator import add_test_plan, connect_test_beneficiary


TEST_PLAN_PARAMS = {
        'totalVestingDuration': 36,
        'vestingCliff': 6,
        'vestingIntervalTimeUnit': 1,
        'vestingInterval': 6,
        'isDelegationAllowed': True,
        'isTerminatable': True
    }


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
    send_ether(skale_allocator.web3, main_wallet, wallet.address, 0.1)

    assert skale_allocator.allocator.is_delegation_allowed(wallet.address)

    assert not skale_allocator.allocator.is_vesting_active(wallet.address)
    skale_allocator.allocator.start_vesting(wallet.address, wait_for=True)
    assert skale_allocator.allocator.is_vesting_active(wallet.address)


def test_stop_vesting(skale_allocator):
    # todo: impove test
    main_wallet = skale_allocator.wallet
    wallet = generate_wallet(skale_allocator.web3)

    connect_test_beneficiary(skale_allocator, D_PLAN_ID, wallet)
    send_ether(skale_allocator.web3, main_wallet, wallet.address, 0.1)

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
    assert beneficiary['startMonth'] == 1
    assert beneficiary['amountAfterLockup'] == 5000000000000000000000


def test_get_plan(skale_allocator):
    plan = skale_allocator.allocator.get_plan(D_PLAN_ID)
    assert plan == TEST_PLAN_PARAMS


def test_get_all_plans(skale_allocator):
    plans = skale_allocator.allocator.get_all_plans()
    plan_params_with_id = TEST_PLAN_PARAMS.copy()
    plan_params_with_id['planId'] = 1
    assert plan_params_with_id == plans[0]
