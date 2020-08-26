""" Tests for skale/allocator/allocator.py """

import time
import datetime
from skale.wallets.web3_wallet import generate_wallet
from skale.utils.account_tools import send_ether, send_tokens

TEST_VESTING_SLIFF = 6
TEST_TOTAL_VESTING_DURATION = 36
TEST_VESTING_INTERVAL_TIME_UNIT = 1
TEST_VESTING_INTERVAL = 6
TEST_CAN_DELEGATE = True
TEST_IS_TERMINATABLE = True

TEST_START_MONTH = int("{:%s}".format(datetime.date(2020, 10, 1)))
TEST_FULL_AMOUNT = 10 ** 10
TEST_LOCKUP_AMOUNT = 10 ** 9

POLL_INTERVAL = 2

TEST_SKALE_AMOUNT = 10 ** 8


def _transfer_tokens_to_allocator(skale, skale_allocator):
    send_tokens(skale, skale_allocator.wallet, skale_allocator.allocator.address, TEST_SKALE_AMOUNT)


def _add_test_plan(skale_allocator, wait_for):
    skale_allocator.allocator.add_plan(
        vesting_cliff=TEST_VESTING_SLIFF,
        total_vesting_duration=TEST_TOTAL_VESTING_DURATION,
        vesting_interval_time_unit=TEST_VESTING_INTERVAL_TIME_UNIT,
        vesting_interval=TEST_VESTING_INTERVAL,
        can_delegate=TEST_CAN_DELEGATE,
        is_terminatable=TEST_IS_TERMINATABLE,
        wait_for=wait_for
    )
    event = catch_event(skale_allocator.allocator.contract.events.PlanCreated)
    return event.args['id']


def _add_plan_and_connect_beneficiary(skale_allocator, wallet):
    plan_id = _add_test_plan(skale_allocator, False)
    skale_allocator.allocator.connect_beneficiary_to_plan(
        beneficiary_address=wallet.address,
        plan_id=plan_id,
        start_month=TEST_START_MONTH,
        full_amount=TEST_FULL_AMOUNT,
        lockup_amount=TEST_LOCKUP_AMOUNT,
        wait_for=True
    )


def _connect_and_approve_beneficiary(skale_allocator, plan_id, wallet):
    skale_allocator.allocator.connect_beneficiary_to_plan(
        beneficiary_address=wallet.address,
        plan_id=plan_id,
        start_month=TEST_START_MONTH,
        full_amount=TEST_FULL_AMOUNT,
        lockup_amount=TEST_LOCKUP_AMOUNT,
        wait_for=True
    )
    main_wallet = skale_allocator.wallet
    skale_allocator.wallet = wallet
    skale_allocator.allocator.approve_address(wait_for=True)
    skale_allocator.wallet = main_wallet


def test_is_beneficiary_registered(skale_allocator):
    wallet = generate_wallet(skale_allocator.web3)
    assert not skale_allocator.allocator.is_beneficiary_registered(wallet.address)


def catch_event(event_obj):
    event_filter = event_obj.createFilter(
        fromBlock=0,
        toBlock='latest'
    )
    while True:
        for event in event_filter.get_new_entries():
            return event
        time.sleep(POLL_INTERVAL)


def test_add_plan(skale_allocator):
    plan_id = _add_test_plan(skale_allocator, False)
    assert isinstance(plan_id, int)


def test_connect_beneficiary_to_plan(skale_allocator):
    wallet = generate_wallet(skale_allocator.web3)
    assert not skale_allocator.allocator.is_beneficiary_registered(wallet.address)
    plan_id = _add_test_plan(skale_allocator, False)
    skale_allocator.allocator.connect_beneficiary_to_plan(
        beneficiary_address=wallet.address,
        plan_id=plan_id,
        start_month=TEST_START_MONTH,
        full_amount=TEST_FULL_AMOUNT,
        lockup_amount=TEST_LOCKUP_AMOUNT,
        wait_for=True
    )
    assert skale_allocator.allocator.is_beneficiary_registered(wallet.address)


def test_approve_address(skale, skale_allocator):
    main_wallet = skale_allocator.wallet
    wallet = generate_wallet(skale_allocator.web3)
    _add_plan_and_connect_beneficiary(skale_allocator, wallet)
    assert skale_allocator.allocator.is_beneficiary_registered(wallet.address)
    assert not skale_allocator.allocator.is_beneficiary_address_approved(wallet.address)

    send_ether(skale_allocator.web3, main_wallet, wallet.address, 0.1)

    skale_allocator.wallet = wallet
    skale_allocator.allocator.approve_address(wait_for=True)

    assert skale_allocator.allocator.is_beneficiary_address_approved(wallet.address)
    assert skale_allocator.allocator.is_delegation_allowed(wallet.address)

    skale_allocator.wallet = main_wallet

    _transfer_tokens_to_allocator(skale, skale_allocator) # todo: move to prepare_data for allocator!!!!
    assert not skale_allocator.allocator.is_vesting_active(wallet.address)
    skale_allocator.allocator.start_vesting(wallet.address, wait_for=True)
    assert skale_allocator.allocator.is_vesting_active(wallet.address)
