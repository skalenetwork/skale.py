"""Tests for contracts/delegation/validator_service.py"""

import random

import pytest

from skale.contracts.manager.delegation.validator_service import FIELDS
from skale.transactions.exceptions import TransactionNotSentError
from skale.transactions.result import DryRunRevertError
from skale.utils.account_tools import send_eth
from skale.utils.contracts_provision.main import _skip_evm_time, enable_validator
from skale.wallets.web3_wallet import generate_wallet
from tests.constants import (
    D_DELEGATION_PERIOD,
    D_VALIDATOR_DESC,
    D_VALIDATOR_FEE,
    D_VALIDATOR_ID,
    D_VALIDATOR_MIN_DEL,
    D_VALIDATOR_NAME,
    MONTH_IN_SECONDS,
    NOT_EXISTING_ID,
)


def link_node_address(skale, wallet, validator_id=D_VALIDATOR_ID):
    main_wallet = skale.wallet
    skale.wallet = wallet
    try:
        signature = skale.validator_service.get_link_node_signature(validator_id=validator_id)
    finally:
        skale.wallet = main_wallet

    skale.validator_service.link_node_address(
        node_address=wallet.address, signature=signature, wait_for=True
    )


def _generate_new_validator(skale, wallet=None, enable=True):
    eth_amount = 10
    main_wallet = skale.wallet
    wallet = wallet or generate_wallet(skale.web3)
    send_eth(skale.web3, main_wallet, wallet.address, eth_amount)
    validator_id = -1
    try:
        skale.wallet = wallet
        skale.validator_service.register_validator(
            name=D_VALIDATOR_NAME,
            description=D_VALIDATOR_DESC,
            fee_rate=D_VALIDATOR_FEE,
            min_delegation_amount=D_VALIDATOR_MIN_DEL,
        )
        validator_id = skale.validator_service.validator_id_by_address(wallet.address)
    finally:
        skale.wallet = main_wallet

    assert validator_id > 0, validator_id
    if enable:
        enable_validator(skale, validator_id)
    return validator_id


def test_get_raw_not_exist(skale):
    empty_struct = skale.validator_service._ValidatorService__get_raw(NOT_EXISTING_ID)
    assert empty_struct[0] == ''
    assert empty_struct[1] == '0x0000000000000000000000000000000000000000'


def test_get(skale, validator):
    validator_id = validator
    validator_data = skale.validator_service.get(validator_id)
    assert list(validator_data.keys()) == FIELDS
    assert [k for k, v in validator_data.items() if v is None] == []


def test_get_with_id(skale):
    validator = skale.validator_service.get_with_id(D_VALIDATOR_ID)
    assert validator['id'] == D_VALIDATOR_ID


def test_number_of_validators(skale):
    n_of_validators_before = skale.validator_service.number_of_validators()
    _generate_new_validator(skale)
    n_of_validators_after = skale.validator_service.number_of_validators()
    assert n_of_validators_after == n_of_validators_before + 1


def test_ls(skale, validator):
    n_of_validators = skale.validator_service.number_of_validators()
    validators = sorted(skale.validator_service.ls(), key=lambda x: x['validator_address'])
    assert n_of_validators == len(validators)
    session_validator_data = skale.validator_service.get_with_id(validator)
    assert session_validator_data in validators
    trusted_validators = sorted(
        skale.validator_service.ls(trusted_only=True), key=lambda x: x['validator_address']
    )
    assert all(v['trusted'] for v in trusted_validators)
    assert list(filter(lambda v: v['trusted'], validators)) == trusted_validators


def test_get_linked_addresses_by_validator_address(skale, validator):
    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        address=skale.wallet.address
    )

    wallet = generate_wallet(skale.web3)
    link_node_address(skale, wallet, validator_id=validator)

    assert wallet.address not in addresses
    addresses_by_address = skale.validator_service.get_linked_addresses_by_validator_address(
        address=skale.wallet.address
    )
    assert wallet.address in addresses_by_address
    addresses_by_id = skale.validator_service.get_linked_addresses_by_validator_id(
        validator_id=validator
    )
    assert addresses_by_address == addresses_by_id


def test_is_main_address(skale, validator):
    is_main_address = skale.validator_service.is_main_address(skale.wallet.address)
    assert is_main_address

    wallet = generate_wallet(skale.web3)
    link_node_address(skale, wallet, validator_id=validator)

    is_main_address = skale.validator_service.is_main_address(wallet.address)
    assert not is_main_address


def test_validator_address_exists(skale):
    address_exists = skale.validator_service.validator_address_exists(skale.wallet.address)
    assert address_exists

    wallet = generate_wallet(skale.web3)
    address_exists = skale.validator_service.validator_address_exists(wallet.address)
    assert not address_exists


def test_validator_exists(skale, validator):
    validator_exists = skale.validator_service.validator_exists(validator_id=validator)
    assert validator_exists
    validator_exists = skale.validator_service.validator_exists(NOT_EXISTING_ID)
    assert not validator_exists


def test_get_validator_node_indices(skale, validator):  # todo: improve test
    node_indices = skale.nodes.get_validator_node_indices(validator_id=validator)
    all_active_node_ids = skale.nodes.get_active_node_ids()
    assert set(all_active_node_ids).issubset(node_indices)


def test_enable_validator(skale):
    validator_id = _generate_new_validator(skale, enable=False)
    is_validator_trusted = skale.validator_service._is_authorized_validator(
        validator_id=validator_id
    )
    assert not is_validator_trusted

    skale.validator_service._enable_validator(validator_id=validator_id)

    is_validator_trusted = skale.validator_service._is_authorized_validator(
        validator_id=validator_id
    )
    assert is_validator_trusted


def test_disable_validator(skale):
    validator_id = _generate_new_validator(skale, enable=True)

    is_validator_trusted = skale.validator_service._is_authorized_validator(
        validator_id=validator_id
    )
    assert is_validator_trusted

    skale.validator_service._disable_validator(validator_id=validator_id)
    is_validator_trusted = skale.validator_service._is_authorized_validator(validator_id)
    assert not is_validator_trusted


def test_is_accepting_new_requests(skale, validator):
    is_accepting_new_requests = skale.validator_service.is_accepting_new_requests(
        validator_id=validator
    )
    assert is_accepting_new_requests


def test_register_existing_validator(skale):
    with pytest.raises(DryRunRevertError):
        skale.validator_service.register_validator(
            name=D_VALIDATOR_NAME,
            description=D_VALIDATOR_DESC,
            fee_rate=D_VALIDATOR_FEE,
            min_delegation_amount=D_VALIDATOR_MIN_DEL,
            wait_for=True,
        )


def test_register_new_validator(skale):
    n_of_validators_before = skale.validator_service.number_of_validators()
    _generate_new_validator(skale)
    n_of_validators_after = skale.validator_service.number_of_validators()
    assert n_of_validators_after == n_of_validators_before + 1


def test_unlink_node_address(skale):
    wallet = generate_wallet(skale.web3)
    link_node_address(skale, wallet)

    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        skale.wallet.address
    )
    assert wallet.address in addresses

    skale.validator_service.unlink_node_address(
        node_address=wallet.address,
    )
    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        skale.wallet.address
    )
    assert wallet.address not in addresses


def test_get_and_update_bond_amount(skale, validator):
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * 3)
    initial_bond = skale.validator_service.get_and_update_bond_amount(validator_id=validator)
    additional_bond = skale.constants_holder.msr() * 2

    # Delegate to myself
    skale.delegation_controller.delegate(
        validator_id=validator,
        amount=additional_bond,
        delegation_period=D_DELEGATION_PERIOD,
        info='Test get_and_update_bond_amount',
        wait_for=True,
    )

    # Accept delegation
    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=validator
    )
    skale.delegation_controller.accept_pending_delegation(
        delegation_id=delegations[-1]['id'], wait_for=True
    )

    initial_bts = skale.web3.eth.get_block('latest').timestamp
    # Skip time
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS)
    bts = skale.web3.eth.get_block('latest').timestamp

    bond = skale.validator_service.get_and_update_bond_amount(validator_id=validator)
    locked = skale.token_state.get_and_update_locked_amount(skale.wallet.address)
    assert bond == initial_bond + additional_bond, (
        bond,
        initial_bond + additional_bond,
        locked,
        initial_bts,
        bts,
    )


def test_set_validator_mda(skale, validator):
    validator_id = validator
    minimum_delegation_amount = random.randint(1000, 10000)

    validator = skale.validator_service.get(validator_id)
    old_mda = validator['minimum_delegation_amount']

    skale.validator_service.set_validator_mda(
        minimum_delegation_amount=minimum_delegation_amount, wait_for=True
    )
    validator = skale.validator_service.get(validator_id)
    new_mda = validator['minimum_delegation_amount']

    assert minimum_delegation_amount != old_mda
    assert minimum_delegation_amount == new_mda


def test_request_confirm_new_address(skale):
    main_wallet = skale.wallet
    try:
        old_wallet = generate_wallet(skale.web3)
        validator_id = _generate_new_validator(skale, wallet=old_wallet)
        skale.wallet = old_wallet
        new_wallet = generate_wallet(skale.web3)
        eth_amount = 10
        skale.wallet = main_wallet
        send_eth(skale.web3, skale.wallet, new_wallet.address, eth_amount)
        validator = skale.validator_service.get(validator_id)
        assert validator['requested_address'] == '0x0000000000000000000000000000000000000000'

        with pytest.raises(DryRunRevertError):
            skale.validator_service.request_for_new_address(
                new_validator_address=main_wallet.address, wait_for=True
            )
        skale.wallet = old_wallet
        skale.validator_service.request_for_new_address(
            new_validator_address=new_wallet.address, wait_for=True
        )
        validator = skale.validator_service.get(validator_id)
        assert validator['requested_address'] == new_wallet.address
        assert validator['validator_address'] == old_wallet.address

        skale.wallet = new_wallet
        skale.validator_service.confirm_new_address(validator_id=validator_id, wait_for=True)
        validator = skale.validator_service.get(validator_id)
        assert validator['requested_address'] == '0x0000000000000000000000000000000000000000'
        assert validator['validator_address'] == new_wallet.address
    finally:
        skale.wallet = main_wallet


def test_set_validator_name(skale):
    main_wallet = skale.wallet
    wallet = generate_wallet(skale.web3)
    validator_id = _generate_new_validator(skale, wallet=wallet)
    try:
        skale.wallet = wallet
        new_test_name = 'test_123'
        validator = skale.validator_service.get(validator_id)
        assert validator['name'] == D_VALIDATOR_NAME
        assert validator['name'] != new_test_name

        skale.validator_service.set_validator_name(new_name=new_test_name, wait_for=True)

        validator = skale.validator_service.get(validator_id)
        assert validator['name'] != D_VALIDATOR_NAME
        assert validator['name'] == new_test_name
    finally:
        skale.wallet = main_wallet


def test_set_validator_description(skale):
    main_wallet = skale.wallet
    wallet = generate_wallet(skale.web3)
    validator_id = _generate_new_validator(skale, wallet=wallet)
    try:
        skale.wallet = wallet
        new_test_description = 'test_description'
        validator = skale.validator_service.get(validator_id)
        assert validator['description'] == D_VALIDATOR_DESC
        assert validator['description'] != new_test_description

        skale.validator_service.set_validator_description(
            new_description=new_test_description, wait_for=True
        )

        validator = skale.validator_service.get(validator_id)
        assert validator['description'] != D_VALIDATOR_DESC
        assert validator['description'] == new_test_description
    finally:
        skale.wallet = main_wallet


def test_revert_register(skale):
    with pytest.raises(TransactionNotSentError):
        skale.validator_service.register_validator(
            name=D_VALIDATOR_NAME,
            description=D_VALIDATOR_DESC,
            fee_rate=D_VALIDATOR_FEE,
            min_delegation_amount=D_VALIDATOR_MIN_DEL,
            wait_for=True,
            skip_dry_run=True,
        )


def test_get_use_whitelist(skale):
    assert skale.validator_service.get_use_whitelist()


@pytest.mark.skip('Breaks whitelist related tests')
def test_disable_whitelist(skale):
    assert skale.validator_service.get_use_whitelist()
    skale.validator_service.disable_whitelist(wait_for=True)
    assert not skale.validator_service.get_use_whitelist()
