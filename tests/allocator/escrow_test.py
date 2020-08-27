""" Tests for skale/allocator/escrow.py """

from skale.wallets.web3_wallet import generate_wallet
from skale.utils.account_tools import send_ether, check_skale_balance

from tests.manager.delegation.delegation_controller_test import _get_number_of_delegations
from tests.allocator.allocator_test import (_add_test_plan, _connect_and_approve_beneficiary,
                                            _transfer_tokens_to_allocator)
from tests.constants import (D_DELEGATION_INFO, D_VALIDATOR_ID,
                             D_DELEGATION_AMOUNT, D_DELEGATION_PERIOD)

from skale.utils.contracts_provision.main import _skip_evm_time
from skale.utils.contracts_provision import MONTH_IN_SECONDS


def _delegate_via_escrow(skale_allocator, plan_id, wallet):
    main_wallet = skale_allocator.wallet
    send_ether(skale_allocator.web3, main_wallet, wallet.address, 0.5)
    _connect_and_approve_beneficiary(skale_allocator, plan_id, wallet)
    skale_allocator.allocator.start_vesting(wallet.address, wait_for=True)
    skale_allocator.wallet = wallet

    skale_allocator.escrow.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        beneficiary_address=skale_allocator.wallet.address,
        wait_for=True
    )
    skale_allocator.wallet = main_wallet


def test_delegate(skale, skale_allocator):
    main_wallet = skale_allocator.wallet
    wallet = generate_wallet(skale_allocator.web3)
    send_ether(skale_allocator.web3, main_wallet, wallet.address, 0.1)

    plan_id = _add_test_plan(skale_allocator, False)
    _connect_and_approve_beneficiary(skale_allocator, plan_id, wallet)

    _transfer_tokens_to_allocator(skale, skale_allocator)  # todo move to prepare_data for allocator
    skale_allocator.allocator.start_vesting(wallet.address, wait_for=True)

    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * 12)

    skale_allocator.wallet = wallet

    num_of_delegations_before = _get_number_of_delegations(skale)
    skale_allocator.escrow.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        beneficiary_address=skale_allocator.wallet.address,
        wait_for=True
    )
    num_of_delegations_after = _get_number_of_delegations(skale)
    assert num_of_delegations_after == num_of_delegations_before + 1

    skale_allocator.wallet = main_wallet


def test_request_undelegate(skale, skale_allocator):
    main_wallet = skale_allocator.wallet
    wallet = generate_wallet(skale_allocator.web3)

    plan_id = _add_test_plan(skale_allocator, False)
    _delegate_via_escrow(skale_allocator, plan_id, wallet)

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=D_VALIDATOR_ID
    )
    delegation_id = delegations[-1]['id']
    skale.delegation_controller.accept_pending_delegation(
        delegation_id,
        wait_for=True
    )

    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * (D_DELEGATION_PERIOD + 1))

    skale_allocator.wallet = wallet
    skale_allocator.escrow.request_undelegation(
        delegation_id,
        beneficiary_address=skale_allocator.wallet.address,
        wait_for=True
    )
    skale_allocator.wallet = main_wallet

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=D_VALIDATOR_ID
    )
    assert delegations[-1]['id'] == delegation_id
    assert delegations[-1]['status'] == 'UNDELEGATION_REQUESTED'


def test_retrieve(skale, skale_allocator):
    main_wallet = skale_allocator.wallet
    wallet = generate_wallet(skale_allocator.web3)

    plan_id = _add_test_plan(skale_allocator, False)
    _delegate_via_escrow(skale_allocator, plan_id, wallet)

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=D_VALIDATOR_ID
    )
    delegation_id = delegations[-1]['id']
    skale.delegation_controller.accept_pending_delegation(
        delegation_id,
        wait_for=True
    )

    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * (D_DELEGATION_PERIOD + 1))

    skale_allocator.wallet = wallet
    skale_allocator.escrow.retrieve(
        beneficiary_address=skale_allocator.wallet.address,
        wait_for=True
    )
    skale_allocator.wallet = main_wallet
    # todo: improve test


def test_withdraw_bounty(skale, skale_allocator):
    main_wallet = skale_allocator.wallet
    wallet = generate_wallet(skale_allocator.web3)

    plan_id = _add_test_plan(skale_allocator, False)
    _delegate_via_escrow(skale_allocator, plan_id, wallet)

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=D_VALIDATOR_ID
    )
    delegation_id = delegations[-1]['id']
    skale.delegation_controller.accept_pending_delegation(
        delegation_id,
        wait_for=True
    )

    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * (D_DELEGATION_PERIOD + 1))

    skale_allocator.wallet = wallet

    check_skale_balance(skale, wallet.address)
    skale_allocator.escrow.withdraw_bounty(
        D_VALIDATOR_ID,
        wallet.address,
        beneficiary_address=skale_allocator.wallet.address,
        wait_for=True
    )
    skale_allocator.wallet = main_wallet
    # todo: improve test
