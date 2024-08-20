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
from typing import Optional

from web3 import Web3

from skale.transactions.tools import compose_eth_transfer_tx
from skale.utils.constants import LONG_LINE
from skale.wallets import LedgerWallet, Web3Wallet
from skale.utils.web3_utils import (
    check_receipt,
    default_gas_price,
    wait_for_confirmation_blocks
)

logger = logging.getLogger(__name__)


WALLET_TYPE_TO_CLASS = {
    'ledger': LedgerWallet,
    'web3': Web3Wallet
}


def create_wallet(wallet_type='web3', *args, **kwargs):
    return WALLET_TYPE_TO_CLASS[wallet_type](*args, **kwargs)


def send_tokens(
    skale,
    receiver_address,
    amount,
    *args,
    **kwargs
):
    logger.info(
        f'Sending {amount} SKALE tokens from {skale.wallet.address} => '
        f'{receiver_address}'
    )

    wei_amount = skale.web3.to_wei(amount, 'ether')
    return skale.token.transfer(
        receiver_address,
        wei_amount,
        *args,
        **kwargs
    )


def send_eth(
    web3: Web3,
    wallet,
    receiver_address,
    amount,
    *args,
    gas_price: Optional[int] = None,
    wait_for: bool = True,
    confirmation_blocks: int = 0,
    multiplier: Optional[int] = None,
    priority: Optional[int] = None,
    **kwargs
):
    logger.info(
        f'Sending {amount} ETH from {wallet.address} => '
        f'{receiver_address}'
    )
    wei_amount = web3.to_wei(amount, 'ether')
    gas_price = gas_price or default_gas_price(web3)
    tx = compose_eth_transfer_tx(
        web3=web3,
        *args,
        gas_price=gas_price,
        from_address=wallet.address,
        to_address=receiver_address,
        value=wei_amount,
        **kwargs
    )
    tx_hash = wallet.sign_and_send(
        tx,
        multiplier=multiplier,
        priority=priority
    )
    if wait_for:
        receipt = wallet.wait(tx_hash)
    if confirmation_blocks:
        wait_for_confirmation_blocks(
            web3,
            confirmation_blocks
        )
    check_receipt(receipt)
    return receipt


def account_eth_balance_wei(web3, address):
    return web3.eth.get_balance(address)


def check_ether_balance(web3, address):
    balance_wei = account_eth_balance_wei(web3, address)
    balance = web3.from_wei(balance_wei, 'ether')

    logger.info(f'{address} balance: {balance} ETH')
    return balance


def check_skale_balance(skale, address):
    balance_wei = skale.token.get_balance(address)
    balance = skale.web3.from_wei(balance_wei, 'ether')
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

        send_tokens(skale, wallet['address'], skale_amount)
        send_eth(skale.web3, skale.wallet, wallet['address'], eth_amount)

        if debug:
            check_ether_balance(skale.web3, wallet['address'])
            check_skale_balance(skale, wallet['address'])

        results.append(wallet)
        logger.info(LONG_LINE)

    return results
