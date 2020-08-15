""" Tests for contracts/delegation/validator_service.py """

import random
import pytest

from skale.manager.contracts.delegation.validator_service import FIELDS
from skale.transactions.result import DryRunFailedError
from skale.utils.web3_utils import check_receipt
from skale.utils.account_tools import send_ether
from skale.wallets.web3_wallet import generate_wallet
from skale.utils.contracts_provision.main import _skip_evm_time

from tests.constants import (
    D_DELEGATION_PERIOD, D_VALIDATOR_ID, D_VALIDATOR_NAME, D_VALIDATOR_DESC,
    D_VALIDATOR_FEE, D_VALIDATOR_MIN_DEL,
    MONTH_IN_SECONDS, NOT_EXISTING_ID
)


def link_node_address(skale, wallet):
    main_wallet = skale.wallet
    skale.wallet = wallet
    signature = skale.validator_service.get_link_node_signature(
        validator_id=D_VALIDATOR_ID
    )
    skale.wallet = main_wallet
    skale.validator_service.link_node_address(
        node_address=wallet.address,
        signature=signature,
        wait_for=True
    )


def test_get_raw_not_exist(skale):
    empty_struct = skale.validator_service._ValidatorService__get_raw(
        NOT_EXISTING_ID)
    assert empty_struct[0] == ''
    assert empty_struct[1] == '0x0000000000000000000000000000000000000000'


def test_get(skale):
    validator = skale.validator_service.get(D_VALIDATOR_ID)
    assert list(validator.keys()) == FIELDS
    assert [k for k, v in validator.items() if v is None] == []


def test_get_with_id(skale):
    validator = skale.validator_service.get_with_id(D_VALIDATOR_ID)
    assert validator['id'] == D_VALIDATOR_ID


def test_number_of_validators(skale):
    n_of_validators_before = skale.validator_service.number_of_validators()
    _generate_new_validator(skale)
    n_of_validators_after = skale.validator_service.number_of_validators()
    assert n_of_validators_after == n_of_validators_before + 1


def test_ls(skale):
    n_of_validators = skale.validator_service.number_of_validators()
    validators = sorted(skale.validator_service.ls(),
                        key=lambda x: x['validator_address'])
    assert all(
        [validator['name'] == D_VALIDATOR_NAME for validator in validators])
    assert n_of_validators == len(validators)
    trusted_validators = sorted(skale.validator_service.ls(trusted_only=True),
                                key=lambda x: x['validator_address'])
    assert trusted_validators == sorted(
        [v for v in validators if v['trusted']], key=lambda x: x['validator_address'])


def test_get_linked_addresses_by_validator_address(skale):
    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        address=skale.wallet.address
    )
    # assert skale.wallet.address in addresses # todo: can't link main address for now

    wallet = generate_wallet(skale.web3)
    link_node_address(skale, wallet)

    assert wallet.address not in addresses
    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        address=skale.wallet.address
    )
    assert wallet.address in addresses


def test_get_linked_addresses_by_validator_id(skale):
    addresses = skale.validator_service.get_linked_addresses_by_validator_id(
        D_VALIDATOR_ID)
    assert isinstance(addresses, list)
    # assert skale.wallet.address in addresses # todo: can't link main address for now


def test_is_main_address(skale):
    is_main_address = skale.validator_service.is_main_address(
        skale.wallet.address)
    assert is_main_address

    wallet = generate_wallet(skale.web3)
    link_node_address(skale, wallet)

    is_main_address = skale.validator_service.is_main_address(wallet.address)
    assert not is_main_address


def test_validator_address_exists(skale):
    address_exists = skale.validator_service.validator_address_exists(
        skale.wallet.address)
    assert address_exists

    wallet = generate_wallet(skale.web3)
    address_exists = skale.validator_service.validator_address_exists(
        wallet.address)
    assert not address_exists


def test_validator_exists(skale):
    validator_exists = skale.validator_service.validator_exists(D_VALIDATOR_ID)
    assert validator_exists
    validator_exists = skale.validator_service.validator_exists(NOT_EXISTING_ID)
    assert not validator_exists


def test_validator_id_by_address(skale):
    validator_id = skale.validator_service.validator_id_by_address(
        skale.wallet.address)
    assert validator_id == D_VALIDATOR_ID


def test_get_validator_node_indices(skale):  # todo: improve test
    node_indices = skale.nodes.get_validator_node_indices(
        validator_id=D_VALIDATOR_ID
    )
    all_active_node_ids = skale.nodes.get_active_node_ids()
    assert set(all_active_node_ids).issubset(node_indices)


def test_enable_validator(skale):
    _generate_new_validator(skale)
    latest_id = skale.validator_service.number_of_validators()

    is_validator_trusted = skale.validator_service._is_authorized_validator(
        latest_id)
    assert not is_validator_trusted

    tx_res = skale.validator_service._enable_validator(
        validator_id=latest_id,
        wait_for=True
    )
    check_receipt(tx_res.receipt)

    is_validator_trusted = skale.validator_service._is_authorized_validator(
        latest_id)
    assert is_validator_trusted


def test_disable_validator(skale):
    _generate_new_validator(skale)
    latest_id = skale.validator_service.number_of_validators()

    is_validator_trusted = skale.validator_service._is_authorized_validator(
        latest_id)
    assert not is_validator_trusted

    tx_res = skale.validator_service._enable_validator(
        validator_id=latest_id,
        wait_for=True
    )
    check_receipt(tx_res.receipt)

    is_validator_trusted = skale.validator_service._is_authorized_validator(
        latest_id)
    assert is_validator_trusted

    tx_res = skale.validator_service._disable_validator(
        validator_id=latest_id,
        wait_for=True
    )
    is_validator_trusted = skale.validator_service._is_authorized_validator(
        latest_id)
    assert not is_validator_trusted


def test_is_authorized_validator(skale):
    is_validator_trusted = skale.validator_service._is_authorized_validator(
        D_VALIDATOR_ID)
    assert is_validator_trusted


def test_is_accepting_new_requests(skale):
    is_accepting_new_requests = skale.validator_service.is_accepting_new_requests(D_VALIDATOR_ID)
    assert is_accepting_new_requests


def test_register_existing_validator(skale):
    with pytest.raises(DryRunFailedError):
        skale.validator_service.register_validator(
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
    tx_res = skale.validator_service.register_validator(
        name=D_VALIDATOR_NAME,
        description=D_VALIDATOR_DESC,
        fee_rate=D_VALIDATOR_FEE,
        min_delegation_amount=D_VALIDATOR_MIN_DEL,
        wait_for=True
    )
    check_receipt(tx_res.receipt)
    skale.wallet = main_wallet
    return wallet


def test_register_new_validator(skale):
    n_of_validators_before = skale.validator_service.number_of_validators()
    _generate_new_validator(skale)
    n_of_validators_after = skale.validator_service.number_of_validators()
    assert n_of_validators_after == n_of_validators_before + 1


def test_link_node_address(skale):
    wallet = generate_wallet(skale.web3)
    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        skale.wallet.address
    )
    assert wallet.address not in addresses

    link_node_address(skale, wallet)

    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        skale.wallet.address
    )
    assert wallet.address in addresses


def test_unlink_node_address(skale):
    wallet = generate_wallet(skale.web3)
    link_node_address(skale, wallet)

    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        skale.wallet.address
    )
    assert wallet.address in addresses

    tx_res = skale.validator_service.unlink_node_address(
        node_address=wallet.address,
        wait_for=True
    )
    check_receipt(tx_res.receipt)
    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        skale.wallet.address
    )
    assert wallet.address not in addresses


def test_get_use_whitelist(skale):
    assert skale.validator_service.get_use_whitelist()


def test_disable_whitelist(skale):
    assert skale.validator_service.get_use_whitelist()
    skale.validator_service.disable_whitelist(wait_for=True)
    assert not skale.validator_service.get_use_whitelist()


def test_get_and_update_bond_amount(skale):
    initial_bond = skale.validator_service.get_and_update_bond_amount(D_VALIDATOR_ID)
    additional_bond = skale.constants_holder.msr() * 2

    # Delegate to myself
    skale.delegation_controller.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=additional_bond,
        delegation_period=D_DELEGATION_PERIOD,
        info='Test get_and_update_bond_amount',
        wait_for=True
    )

    # Accept delegation
    delegations = skale.delegation_controller.get_all_delegations_by_validator(D_VALIDATOR_ID)
    skale.delegation_controller.accept_pending_delegation(
        delegation_id=delegations[-1]['id'],
        wait_for=True
    )

    # Skip time
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS)

    bond = skale.validator_service.get_and_update_bond_amount(D_VALIDATOR_ID)
    locked = skale.token_state.get_and_update_locked_amount(skale.wallet.address)
    print(delegations)
    assert bond == initial_bond + additional_bond, (bond, initial_bond + additional_bond, locked)


def test_set_validator_mda(skale):
    minimum_delegation_amount = random.randint(1000, 10000)

    validator = skale.validator_service.get(D_VALIDATOR_ID)
    old_mda = validator['minimum_delegation_amount']

    skale.validator_service.set_validator_mda(
        minimum_delegation_amount=minimum_delegation_amount,
        wait_for=True
    )
    validator = skale.validator_service.get(D_VALIDATOR_ID)
    new_mda = validator['minimum_delegation_amount']

    assert minimum_delegation_amount != old_mda
    assert minimum_delegation_amount == new_mda


def test_request_for_new_address(skale):
    main_wallet = skale.wallet
    skale.wallet = _generate_new_validator(skale)
    new_wallet = generate_wallet(skale.web3)

    validator = skale.validator_service.get(D_VALIDATOR_ID)
    assert validator['requested_address'] == '0x0000000000000000000000000000000000000000'

    with pytest.raises(DryRunFailedError):
        skale.validator_service.request_for_new_address(
            new_validator_address=main_wallet.address,
            wait_for=True
        )

    skale.validator_service.request_for_new_address(
        new_validator_address=new_wallet.address,
        wait_for=True
    )

    n_of_validators = skale.validator_service.number_of_validators()
    validator = skale.validator_service.get(n_of_validators)
    assert validator['requested_address'] == new_wallet.address

    skale.wallet = main_wallet


def test_confirm_new_address(skale):
    main_wallet = skale.wallet
    skale.wallet = _generate_new_validator(skale)
    new_wallet = generate_wallet(skale.web3)
    send_ether(skale.web3, main_wallet, new_wallet.address, 0.1)

    skale.validator_service.request_for_new_address(
        new_validator_address=new_wallet.address,
        wait_for=True
    )

    skale.wallet = new_wallet
    n_of_validators = skale.validator_service.number_of_validators()

    skale.validator_service.confirm_new_address(
        validator_id=n_of_validators,
        wait_for=True
    )

    validator = skale.validator_service.get(n_of_validators)
    assert validator['validator_address'] == new_wallet.address
