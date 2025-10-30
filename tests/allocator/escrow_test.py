"""Tests for skale/allocator/escrow.py"""

from skale.types.delegation import DelegationStatus
from skale.utils.account_tools import check_skale_balance, send_eth
from skale.utils.contracts_provision import D_PLAN_ID, MONTH_IN_SECONDS
from skale.utils.contracts_provision.allocator import connect_test_beneficiary
from skale.utils.contracts_provision.main import _skip_evm_time
from skale.wallets.web3_wallet import generate_wallet
from tests.constants import (
    D_DELEGATION_AMOUNT,
    D_DELEGATION_INFO,
    D_DELEGATION_PERIOD,
    D_VALIDATOR_ID,
)
from tests.manager.delegation.delegation_controller_test import _get_number_of_delegations


def _delegate_via_escrow(skale_allocator, wallet):
    main_wallet = skale_allocator.wallet
    send_eth(skale_allocator.web3, main_wallet, wallet.address, 0.5)
    connect_test_beneficiary(skale_allocator, D_PLAN_ID, wallet)

    skale_allocator.allocator.start_vesting(wallet.address, wait_for=True)
    skale_allocator.wallet = wallet

    skale_allocator.escrow.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        beneficiary_address=skale_allocator.wallet.address,
        wait_for=True,
    )
    skale_allocator.wallet = main_wallet


def test_delegate(skale, skale_allocator):
    main_wallet = skale_allocator.wallet
    wallet = generate_wallet(skale_allocator.web3)
    send_eth(skale_allocator.web3, main_wallet, wallet.address, 0.1)

    connect_test_beneficiary(skale_allocator, D_PLAN_ID, wallet)
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
        wait_for=True,
    )
    num_of_delegations_after = _get_number_of_delegations(skale)
    assert num_of_delegations_after == num_of_delegations_before + 1

    skale_allocator.wallet = main_wallet


def test_request_undelegate(skale, skale_allocator):
    main_wallet = skale_allocator.wallet
    wallet = generate_wallet(skale_allocator.web3)

    _delegate_via_escrow(skale_allocator, wallet)

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=D_VALIDATOR_ID
    )
    delegation_id = delegations[-1]['id']
    skale.delegation_controller.accept_pending_delegation(delegation_id, wait_for=True)

    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * (D_DELEGATION_PERIOD + 1))

    skale_allocator.wallet = wallet
    skale_allocator.escrow.request_undelegation(
        delegation_id, beneficiary_address=skale_allocator.wallet.address, wait_for=True
    )
    skale_allocator.wallet = main_wallet

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=D_VALIDATOR_ID
    )
    assert delegations[-1]['id'] == delegation_id
    assert delegations[-1]['status'] == DelegationStatus.UNDELEGATION_REQUESTED


def test_retrieve(skale, skale_allocator):
    main_wallet = skale_allocator.wallet
    wallet = generate_wallet(skale_allocator.web3)

    _delegate_via_escrow(skale_allocator, wallet)

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=D_VALIDATOR_ID
    )
    delegation_id = delegations[-1]['id']
    skale.delegation_controller.accept_pending_delegation(delegation_id, wait_for=True)

    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * (D_DELEGATION_PERIOD + 1))

    skale_allocator.wallet = wallet
    skale_allocator.escrow.retrieve(
        beneficiary_address=skale_allocator.wallet.address, wait_for=True
    )
    skale_allocator.wallet = main_wallet
    # todo: improve test


def test_withdraw_bounty(skale, skale_allocator):
    main_wallet = skale_allocator.wallet
    wallet = generate_wallet(skale_allocator.web3)

    _delegate_via_escrow(skale_allocator, wallet)

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=D_VALIDATOR_ID
    )
    delegation_id = delegations[-1]['id']
    skale.delegation_controller.accept_pending_delegation(delegation_id, wait_for=True)

    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * (D_DELEGATION_PERIOD + 1))

    skale_allocator.wallet = wallet

    check_skale_balance(skale, wallet.address)
    skale_allocator.escrow.withdraw_bounty(
        D_VALIDATOR_ID,
        wallet.address,
        beneficiary_address=skale_allocator.wallet.address,
        wait_for=True,
    )
    skale_allocator.wallet = main_wallet
    # todo: improve test


def test_cancel_pending_delegation(skale_allocator, skale):
    main_wallet = skale_allocator.wallet
    wallet = generate_wallet(skale_allocator.web3)

    _delegate_via_escrow(skale_allocator, wallet)

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=D_VALIDATOR_ID
    )
    delegation_id = delegations[-1]['id']
    skale_allocator.wallet = wallet

    skale_allocator.escrow.cancel_pending_delegation(
        delegation_id=delegation_id,
        beneficiary_address=skale_allocator.wallet.address,
        wait_for=True,
    )
    skale_allocator.wallet = main_wallet

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=D_VALIDATOR_ID
    )
    assert delegations[-1]['id'] == delegation_id
    assert delegations[-1]['status'] == DelegationStatus.CANCELED
