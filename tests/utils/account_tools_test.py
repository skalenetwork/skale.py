""" SKALE account tools test """

from skale.utils.account_tools import (check_ether_balance, generate_account,
                                       generate_accounts, send_ether,
                                       send_tokens, check_skale_balance)
from tests.constants import (TOKEN_TRANSFER_VALUE,
                             ETH_TRANSFER_VALUE,
                             N_TEST_WALLETS)


def test_send_tokens(skale, empty_account):
    sender_balance = skale.token.get_balance(skale.wallet.address)

    send_tokens(skale, skale.wallet, empty_account.address,
                TOKEN_TRANSFER_VALUE)

    receiver_balance_after = skale.token.get_balance(empty_account.address)
    sender_balance_after = skale.token.get_balance(skale.wallet.address)

    token_transfer_value_wei = skale.web3.toWei(TOKEN_TRANSFER_VALUE, 'ether')

    assert receiver_balance_after == token_transfer_value_wei
    assert sender_balance_after == sender_balance - token_transfer_value_wei


def test_send_ether(skale, empty_account):
    sender_balance = check_ether_balance(skale.web3, skale.wallet.address)

    send_ether(skale.web3, skale.wallet, empty_account.address,
               ETH_TRANSFER_VALUE)

    receiver_balance_after = check_ether_balance(skale.web3,
                                                 empty_account.address)
    sender_balance_after = check_ether_balance(skale.web3, skale.wallet.address)

    assert receiver_balance_after == ETH_TRANSFER_VALUE
    # check that sender_balance_after
    # have decreased by ETH_TRANSFER_VALUE and some gas
    assert sender_balance - 2 * ETH_TRANSFER_VALUE < sender_balance_after < \
        sender_balance - ETH_TRANSFER_VALUE


def test_generate_account(skale):
    account = generate_account(skale.web3)
    assert account.get('address') is not None
    assert account.get('private_key') is not None


def test_generate_accounts(skale):
    results = generate_accounts(
        skale,
        skale.wallet,
        N_TEST_WALLETS,
        TOKEN_TRANSFER_VALUE,
        ETH_TRANSFER_VALUE,
        debug=True
    )
    assert len(results) == N_TEST_WALLETS

    test_address = results[-1]['address']
    eth_balance = check_ether_balance(skale.web3, test_address)
    token_balance_test = check_skale_balance(skale, test_address)
    token_balance = skale.token.get_balance(test_address)

    token_transfer_value_wei = skale.web3.toWei(TOKEN_TRANSFER_VALUE, 'ether')

    assert TOKEN_TRANSFER_VALUE == token_balance_test
    assert eth_balance == ETH_TRANSFER_VALUE
    assert token_balance == token_transfer_value_wei
