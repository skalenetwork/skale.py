""" Tests for contracts/delegation/delegation_service.py """

import pytest

from skale.utils.web3_utils import check_receipt
from skale.utils.account_tools import send_ether
from skale.wallets.web3_wallet import generate_wallet

from tests.constants import (
    D_VALIDATOR_NAME, D_VALIDATOR_DESC, D_VALIDATOR_FEE, D_VALIDATOR_MIN_DEL
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
