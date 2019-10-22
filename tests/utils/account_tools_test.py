#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" SKALE account tools test """

from web3 import Web3

from skale.utils.account_tools import (check_ether_balance, generate_account,
                                       generate_accounts, init_wallet,
                                       send_ether, send_tokens, check_skale_balance)
from skale.utils.helper import private_key_to_address
from tests.constants import TOKEN_TRANSFER_VALUE, ETH_TRANSFER_VALUE, N_TEST_WALLETS


def test_init_wallet():
    wallet = init_wallet()
    assert wallet.get('address') is not None
    assert wallet.get('private_key') is not None

    address_fx = Web3.toChecksumAddress(wallet['address'])
    address_from_pk = private_key_to_address(wallet['private_key'])
    assert Web3.toChecksumAddress(address_from_pk) == address_fx


def test_send_tokens(skale, wallet, empty_account):
    sender_balance = skale.token.get_balance(wallet['address'])

    send_tokens(skale, wallet, empty_account.address, TOKEN_TRANSFER_VALUE)

    receiver_balance_after = skale.token.get_balance(empty_account.address)
    sender_balance_after = skale.token.get_balance(wallet['address'])

    token_transfer_value_wei = skale.web3.toWei(TOKEN_TRANSFER_VALUE, 'ether')

    assert receiver_balance_after == token_transfer_value_wei
    assert sender_balance_after == sender_balance - token_transfer_value_wei


def test_send_ether(skale, wallet, empty_account):
    sender_balance = check_ether_balance(skale.web3, wallet['address'])

    send_ether(skale.web3, wallet, empty_account.address, ETH_TRANSFER_VALUE)

    receiver_balance_after = check_ether_balance(skale.web3,
                                                 empty_account.address)
    sender_balance_after = check_ether_balance(skale.web3, wallet['address'])

    assert receiver_balance_after == ETH_TRANSFER_VALUE
    # check that sender_balance_after
    # have decreased by ETH_TRANSFER_VALUE and some gas
    assert sender_balance - 2 * ETH_TRANSFER_VALUE < sender_balance_after < \
        sender_balance - ETH_TRANSFER_VALUE


def test_generate_account(skale):
    account = generate_account(skale.web3)
    assert account.get('address') is not None
    assert account.get('private_key') is not None


def test_generate_accounts(skale, wallet):
    results = generate_accounts(
        skale,
        wallet,
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
