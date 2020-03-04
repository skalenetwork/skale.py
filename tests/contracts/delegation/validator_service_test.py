""" Tests for contracts/delegation/validator_service.py """

from skale.contracts.delegation.validator_service import FIELDS
from skale.wallets.web3_wallet import generate_wallet
from skale.utils.web3_utils import check_receipt

from tests.contracts.delegation.delegation_service_test import _generate_new_validator
from tests.constants import NOT_EXISTING_ID, D_VALIDATOR_ID, D_VALIDATOR_NAME


def test_get_raw_not_exist(skale):
    empty_struct = skale.validator_service._ValidatorService__get_raw(NOT_EXISTING_ID)
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
    validators = skale.validator_service.ls()
    assert all([validator['name'] == D_VALIDATOR_NAME for validator in validators])
    assert n_of_validators == len(validators)
    trusted_validators = skale.validator_service.ls(trusted_only=True)
    assert trusted_validators == [v for v in validators if v['trusted']]


def test_get_linked_addresses_by_validator_address(skale):
    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        address=skale.wallet.address
    )
    assert skale.wallet.address in addresses

    wallet = generate_wallet(skale.web3)
    tx_res = skale.delegation_service.link_node_address(
        node_address=wallet.address,
        wait_for=True
    )
    check_receipt(tx_res.receipt)

    assert wallet.address not in addresses
    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        address=skale.wallet.address
    )
    assert wallet.address in addresses


def test_get_linked_addresses_by_validator_id(skale):
    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        address=skale.wallet.address
    )
    assert skale.wallet.address in addresses


def test_is_main_address(skale):
    is_main_address = skale.validator_service.is_main_address(skale.wallet.address)
    assert is_main_address

    wallet = generate_wallet(skale.web3)
    tx_res = skale.delegation_service.link_node_address(
        node_address=wallet.address,
        wait_for=True
    )
    check_receipt(tx_res.receipt)

    is_main_address = skale.validator_service.is_main_address(wallet.address)
    assert not is_main_address


def test_validator_address_exists(skale):
    address_exists = skale.validator_service.validator_address_exists(skale.wallet.address)
    assert address_exists

    wallet = generate_wallet(skale.web3)
    address_exists = skale.validator_service.validator_address_exists(wallet.address)
    assert not address_exists


def test_validator_id_by_address(skale):
    validator_id = skale.validator_service.validator_id_by_address(skale.wallet.address)
    assert validator_id == D_VALIDATOR_ID


def test_get_validator_node_indices(skale):
    node_indices = skale.validator_service.get_validator_node_indices(
        validator_id=D_VALIDATOR_ID
    )
    assert 0 in node_indices
    assert 1 in node_indices


def test_enable_validator(skale):
    _generate_new_validator(skale)
    latest_id = skale.validator_service.number_of_validators()

    is_validator_trusted = skale.validator_service._is_validator_trusted(latest_id)
    assert not is_validator_trusted

    tx_res = skale.validator_service._enable_validator(
        validator_id=latest_id,
        wait_for=True
    )
    check_receipt(tx_res.receipt)

    is_validator_trusted = skale.validator_service._is_validator_trusted(latest_id)
    assert is_validator_trusted


def test_disable_validator(skale):
    _generate_new_validator(skale)
    latest_id = skale.validator_service.number_of_validators()

    is_validator_trusted = skale.validator_service._is_validator_trusted(latest_id)
    assert not is_validator_trusted

    tx_res = skale.validator_service._enable_validator(
        validator_id=latest_id,
        wait_for=True
    )
    check_receipt(tx_res.receipt)

    is_validator_trusted = skale.validator_service._is_validator_trusted(latest_id)
    assert is_validator_trusted

    tx_res = skale.validator_service._disable_validator(
        validator_id=latest_id,
        wait_for=True
    )
    is_validator_trusted = skale.validator_service._is_validator_trusted(latest_id)
    assert not is_validator_trusted


def test_is_validator_trusted(skale):
    is_validator_trusted = skale.validator_service._is_validator_trusted(D_VALIDATOR_ID)
    assert is_validator_trusted
