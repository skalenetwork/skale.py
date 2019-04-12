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
""" Account utilities """

import logging
import os

from web3 import Web3

import skale.utils.helper as Helper
from skale.utils.constants import LONG_LINE
from skale.utils.helper import private_key_to_address

logger = logging.getLogger(__name__)


def init_wallet(private_key=None):
    base_pr = private_key or os.environ['ETH_PRIVATE_KEY']
    address = private_key_to_address(base_pr)
    address_fx = Web3.toChecksumAddress(address)
    return {'address': address_fx, 'private_key': base_pr}


def init_test_wallet():
    return init_wallet(os.environ['TEST_ETH_PRIVATE_KEY'])


def send_tokens(skale, sender_wallet, receiver_account, amount, await=True):
    logger.info(
        f'Sending {amount} SKALE tokens from {sender_wallet["address"]} => {receiver_account}'
    )

    wei_amount = skale.web3.toWei(amount, 'ether')
    res = skale.token.transfer(receiver_account, wei_amount, sender_wallet)
    if await:
        receipt = Helper.await_receipt(skale.web3, res['tx'])
        Helper.check_receipt(receipt)
        return receipt
    return res['tx']


def send_ether(web3, sender_wallet, receiver_account, amount, await=True):
    logger.info(
        f'Sending {amount} ETH from {sender_wallet["address"]} => {receiver_account}'
    )

    wei_amount = web3.toWei(amount, 'ether')
    tx = Helper.send_eth(web3, receiver_account, wei_amount, sender_wallet)
    if await:
        receipt = Helper.await_receipt(web3, tx)
        Helper.check_receipt(receipt)
        return receipt
    return tx


def check_ether_balance(web3, address):
    balance_wei = web3.eth.getBalance(address)
    balance = web3.fromWei(balance_wei, 'ether')

    logger.info(f'{address} balance: {balance} ETH')
    return balance


def check_skale_balance(skale, address):
    balance_wei = skale.token.get_balance(address)
    balance = skale.web3.fromWei(balance_wei, 'ether')
    logger.info(f'{address} balance: {balance} SKALE')
    return balance


def generate_account(web3):
    account = web3.eth.account.create()
    private_key = account.privateKey.hex()
    logger.info(f'Generated account: {account.address}')
    return {'address': account.address, 'private_key': private_key}


def generate_accounts(skale,
                      base_wallet,
                      n_wallets,
                      skale_amount,
                      eth_amount,
                      debug=False):
    n_wallets = int(n_wallets)
    results = []

    for i in range(0, n_wallets):
        wallet = generate_account(skale.web3)

        send_tokens(skale, base_wallet, wallet['address'], skale_amount)
        send_ether(skale.web3, base_wallet, wallet['address'], eth_amount)

        if debug:
            check_ether_balance(skale.web3, wallet['address'])
            check_skale_balance(skale, wallet['address'])

        results.append(wallet)
        logger.info(LONG_LINE)

    return results
