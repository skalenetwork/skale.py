""" Tests for contracts/delegation/delegation_service.py """

import pytest

from skale.utils.web3_utils import check_receipt
from skale.dataclasses.delegation_status import DelegationStatus
from skale.utils.account_tools import send_ether
from skale.wallets.web3_wallet import generate_wallet

from tests.constants import (
    D_VALIDATOR_NAME, D_VALIDATOR_DESC, D_VALIDATOR_FEE, D_VALIDATOR_MIN_DEL, D_VALIDATOR_ID,
    D_DELEGATION_AMOUNT, D_DELEGATION_PERIOD, D_DELEGATION_INFO
)


def test_register_existing_validator(skale):
    with pytest.raises(ValueError):
        skale.delegation_service.register_validator(
            name=D_VALIDATOR_NAME,
            description=D_VALIDATOR_DESC,
            fee_rate=D_VALIDATOR_FEE,
            min_delegation_amount=D_VALIDATOR_MIN_DEL,
            wait_for=True
        )


def _generate_new_validator(skale):
    eth_amount = 0.1
    main_wallet = skale.wallet
    wallet = generate_wallet(skale.web3)
    send_ether(skale.web3, skale.wallet, wallet.address, eth_amount)
    skale.wallet = wallet
    tx_res = skale.delegation_service.register_validator(
        name=D_VALIDATOR_NAME,
        description=D_VALIDATOR_DESC,
        fee_rate=D_VALIDATOR_FEE,
        min_delegation_amount=D_VALIDATOR_MIN_DEL,
        wait_for=True
    )
    check_receipt(tx_res.receipt)
    skale.wallet = main_wallet


def test_register_new_validator(skale):
    n_of_validators_before = skale.validator_service.number_of_validators()
    _generate_new_validator(skale)
    n_of_validators_after = skale.validator_service.number_of_validators()
    assert n_of_validators_after == n_of_validators_before + 1


def _get_number_of_pending_delegations(skale):
    return len(_get_pending_delegations(skale))


def _get_pending_delegations(skale):
    return skale.delegation_service._get_delegation_ids_by_validator(
        skale.wallet.address,
        DelegationStatus.PROPOSED
    )


def test_delegate(skale):
    num_of_delegations_before = _get_number_of_pending_delegations(skale)
    tx_res = skale.delegation_service.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True
    )
    check_receipt(tx_res.receipt)
    num_of_delegations_after = _get_number_of_pending_delegations(skale)
    assert num_of_delegations_after == num_of_delegations_before + 1

    pending_delegations = skale.delegation_service.get_all_delegations_by_validator(
        skale.wallet.address
    )
    assert pending_delegations[-1]['info'] == D_DELEGATION_INFO


def test_get_delegations(skale):
    delegations = skale.delegation_service.get_delegations(
        skale.wallet.address,
        DelegationStatus.PROPOSED,
        'validator'
    )
    assert delegations[0]['status'] == 'PROPOSED'
    assert delegations[0]['validator_id'] == D_VALIDATOR_ID


def test_get_all_delegations_by_holder(skale):
    delegations = skale.delegation_service.get_all_delegations_by_holder(
        skale.wallet.address
    )
    assert all([delegation['address'] == skale.wallet.address for delegation in delegations])


def test_get_all_delegations_by_validator(skale):
    delegations = skale.delegation_service.get_all_delegations_by_validator(
        skale.wallet.address
    )
    assert all([delegation['validator_id'] == D_VALIDATOR_ID for delegation in delegations])


def test_accept_pending_delegation(skale):
    tx_res = skale.delegation_service.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True
    )
    check_receipt(tx_res.receipt)
    delegations = skale.delegation_service.get_delegations(
        skale.wallet.address,
        DelegationStatus.PROPOSED,
        'validator'
    )
    delegation_id = delegations[-1]['id']
    tx_res = skale.delegation_service.accept_pending_delegation(
        delegation_id,
        wait_for=True
    )
    check_receipt(tx_res.receipt)
    delegations = skale.delegation_service.get_delegations(
        skale.wallet.address,
        DelegationStatus.ACCEPTED,
        'validator'
    )
    assert delegations[-1]['id'] == delegation_id


def test_link_node_address(skale):
    wallet = generate_wallet(skale.web3)
    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        skale.wallet.address
    )
    assert wallet.address not in addresses

    tx_res = skale.delegation_service.link_node_address(
        node_address=wallet.address,
        wait_for=True
    )
    check_receipt(tx_res.receipt)

    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        skale.wallet.address
    )
    assert wallet.address in addresses


def test_unlink_node_address(skale):
    wallet = generate_wallet(skale.web3)
    tx_res = skale.delegation_service.link_node_address(
        node_address=wallet.address,
        wait_for=True
    )
    check_receipt(tx_res.receipt)

    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        skale.wallet.address
    )
    assert wallet.address in addresses

    tx_res = skale.delegation_service.unlink_node_address(
        node_address=wallet.address,
        wait_for=True
    )
    check_receipt(tx_res.receipt)
    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        skale.wallet.address
    )
    assert wallet.address not in addresses


def test_cancel_pending_delegation(skale):
    tx_res = skale.delegation_service.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True
    )
    check_receipt(tx_res.receipt)
    delegations = skale.delegation_service.get_delegations(
        skale.wallet.address,
        DelegationStatus.PROPOSED,
        'validator'
    )
    delegation_id = delegations[-1]['id']
    tx_res = skale.delegation_service.cancel_pending_delegation(
        delegation_id,
        wait_for=True
    )
    check_receipt(tx_res.receipt)
    delegations = skale.delegation_service.get_delegations(
        skale.wallet.address,
        DelegationStatus.COMPLETED,
        'validator'
    )
    assert delegations[-1]['id'] == delegation_id


@pytest.mark.skip('Investigate: revert Message sender is invalid')
def test_get_delegated_amount(skale):  # todo: fix test
    delegated_amount = skale.delegation_service.get_delegated_amount(
        validator_id=D_VALIDATOR_ID
    )
    assert isinstance(delegated_amount, int)


def test_get_delegated_of(skale):  # todo: improve test
    delegated_amount = skale.delegation_service.get_delegated_of(
        address=skale.wallet.address
    )
    assert isinstance(delegated_amount, int)


def test_withdraw_bounty(skale):  # todo: improve test
    tx_res = skale.delegation_service.withdraw_bounty(
        bounty_collection_address=skale.wallet.address,
        amount=0,
        wait_for=True
    )
    check_receipt(tx_res.receipt)


def test_get_earned_bounty_amount(skale):  # todo: improve test
    earned_bounty_amount = skale.delegation_service.get_earned_bounty_amount(
        address=skale.wallet.address
    )
    assert isinstance(earned_bounty_amount, int)
