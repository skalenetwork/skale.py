"""SKALE account tools test"""

from unittest import mock

from skale.utils.account_tools import (
    check_ether_balance,
    check_skale_balance,
    generate_account,
    generate_accounts,
    send_eth,
    send_tokens,
)
from skale.utils.constants import GAS_PRICE_COEFFICIENT
from skale.utils.web3_utils import get_eth_nonce
from skale.wallets.web3_wallet import Web3Wallet, generate_wallet
from tests.constants import ETH_TRANSFER_VALUE, N_TEST_WALLETS, TOKEN_TRANSFER_VALUE


def test_send_tokens(skale, empty_account):
    sender_balance = skale.token.get_balance(skale.wallet.address)

    send_tokens(skale, empty_account.address, TOKEN_TRANSFER_VALUE)

    receiver_balance_after = skale.token.get_balance(empty_account.address)
    sender_balance_after = skale.token.get_balance(skale.wallet.address)

    token_transfer_value_wei = skale.web3.to_wei(TOKEN_TRANSFER_VALUE, 'ether')

    assert receiver_balance_after == token_transfer_value_wei
    assert sender_balance_after == sender_balance - token_transfer_value_wei


def test_send_eth(skale, empty_account):
    sender_balance = check_ether_balance(skale.web3, skale.wallet.address)

    send_eth(skale.web3, skale.wallet, empty_account.address, ETH_TRANSFER_VALUE)

    receiver_balance_after = check_ether_balance(skale.web3, empty_account.address)
    sender_balance_after = check_ether_balance(skale.web3, skale.wallet.address)

    assert receiver_balance_after == ETH_TRANSFER_VALUE
    # check that sender_balance_after
    # have decreased by ETH_TRANSFER_VALUE and some gas
    assert (
        sender_balance - 2 * ETH_TRANSFER_VALUE
        < sender_balance_after
        < sender_balance - ETH_TRANSFER_VALUE
    )


def test_send_eth_with_gas_price(skale, empty_account, block_in_seconds):
    def get_signed_tx_with_custom_gas_price(gas_price):
        wei_amount = skale.web3.to_wei(ETH_TRANSFER_VALUE, 'ether')
        return skale.wallet.sign(
            {
                'to': empty_account.address,
                'value': wei_amount,
                'gasPrice': gas_price,
                'gas': 22000,
                'nonce': get_eth_nonce(skale.web3, skale.wallet.address),
            }
        )

    custom_default_gas_price = 101 * 10**9
    with mock.patch(
        'skale.utils.account_tools.default_gas_price', return_value=custom_default_gas_price
    ):
        receipt = send_eth(
            skale.web3, skale.wallet, empty_account.address, ETH_TRANSFER_VALUE, wait_for=True
        )
        assert receipt['effectiveGasPrice'] == custom_default_gas_price

    # Send ether with default avg gas price
    avg_gas_price = skale.web3.eth.gas_price * GAS_PRICE_COEFFICIENT
    receipt = send_eth(
        skale.web3, skale.wallet, empty_account.address, ETH_TRANSFER_VALUE, wait_for=True
    )
    assert receipt['effectiveGasPrice'] == avg_gas_price


def test_generate_account(skale):
    account = generate_account(skale.web3)
    assert account.get('address') is not None
    assert account.get('private_key') is not None


def test_generate_accounts(skale):
    results = generate_accounts(
        skale, skale.wallet, N_TEST_WALLETS, TOKEN_TRANSFER_VALUE, ETH_TRANSFER_VALUE, debug=True
    )
    assert len(results) == N_TEST_WALLETS

    test_address = results[-1]['address']
    eth_balance = check_ether_balance(skale.web3, test_address)
    token_balance_test = check_skale_balance(skale, test_address)
    token_balance = skale.token.get_balance(test_address)

    token_transfer_value_wei = skale.web3.to_wei(TOKEN_TRANSFER_VALUE, 'ether')

    assert TOKEN_TRANSFER_VALUE == token_balance_test
    assert eth_balance == ETH_TRANSFER_VALUE
    assert token_balance == token_transfer_value_wei


def test_generate_wallet(skale):
    wallet = generate_wallet(skale.web3)
    assert isinstance(wallet, Web3Wallet)
    assert wallet.address
    assert wallet.address != skale.wallet.address
