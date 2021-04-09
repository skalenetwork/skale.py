#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019-Present SKALE Labs
#
#   SKALE.py is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   SKALE.py is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with SKALE.py.  If not, see <https://www.gnu.org/licenses/>.
""" Account utilities """

import logging

from skale.transactions.tools import send_eth
from skale.utils.constants import LONG_LINE
from skale.wallets import LedgerWallet, Web3Wallet
from skale.utils.web3_utils import check_receipt, wait_for_receipt_by_blocks

logger = logging.getLogger(__name__)


WALLET_TYPE_TO_CLASS = {
    'ledger': LedgerWallet,
    'web3': Web3Wallet
}


def create_wallet(wallet_type='web3', *args, **kwargs):
    return WALLET_TYPE_TO_CLASS[wallet_type](*args, **kwargs)


def send_tokens(skale, sender_wallet, receiver_account, amount,
                wait_for=True):
    logger.info(
        f'Sending {amount} SKALE tokens from {sender_wallet.address} => '
        f'{receiver_account}'
    )

    wei_amount = skale.web3.toWei(amount, 'ether')
    tx_res = skale.token.transfer(receiver_account, wei_amount, wait_for=wait_for)
    if wait_for:
        check_receipt(tx_res.receipt)
    return tx_res


def send_ether(web3, sender_wallet, receiver_account, amount,
               gas_price=None, wait_for=True):
    logger.info(
        f'Sending {amount} ETH from {sender_wallet.address} => '
        f'{receiver_account}'
    )

    wei_amount = web3.toWei(amount, 'ether')
    tx = send_eth(web3, receiver_account, wei_amount, sender_wallet,
                  gas_price=gas_price)
    if wait_for:
        receipt = wait_for_receipt_by_blocks(web3, tx)
        check_receipt(receipt)
        return receipt
    else:  # pragma: no cover
        return tx


def account_eth_balance_wei(web3, address):
    return web3.eth.getBalance(address)


def check_ether_balance(web3, address):
    balance_wei = account_eth_balance_wei(web3, address)
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
    private_key = account.key.hex()
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

    for _ in range(0, n_wallets):
        wallet = generate_account(skale.web3)

        send_tokens(skale, skale.wallet, wallet['address'], skale_amount)
        send_ether(skale.web3, skale.wallet, wallet['address'], eth_amount)

        if debug:
            check_ether_balance(skale.web3, wallet['address'])
            check_skale_balance(skale, wallet['address'])

        results.append(wallet)
        logger.info(LONG_LINE)

    return results
