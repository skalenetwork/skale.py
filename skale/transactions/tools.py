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

import logging

from skale.utils.web3_utils import get_eth_nonce

logger = logging.getLogger(__name__)


def build_tx_dict(method, gas_limit, gas_price=None, nonce=None):
    tx_dict_fields = {
        'gas': gas_limit,
        'nonce': nonce
    }
    if gas_price is not None:
        tx_dict_fields.update({'gasPrice': gas_price})

    return method.buildTransaction(tx_dict_fields)


def post_transaction(wallet, method, gas_limit, gas_price=None, nonce=None):
    tx_dict = build_tx_dict(method, gas_limit, gas_price, nonce)
    return wallet.sign_and_send(tx_dict)


def sign_and_send(web3, method, gas_amount, wallet):
    nonce = get_eth_nonce(web3, wallet.address)
    tx_dict = build_tx_dict(method, gas_amount, nonce)
    signed_tx = wallet.sign(tx_dict)
    tx = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    return tx


def send_eth(web3, account, amount, wallet):
    eth_nonce = get_eth_nonce(web3, wallet.address)
    logger.info(f'Transaction nonce {eth_nonce}')
    txn = {
        'to': account,
        'from': wallet.address,
        'value': amount,
        'gasPrice': web3.eth.gasPrice,
        'gas': 22000,
        'nonce': eth_nonce
    }
    signed_txn = wallet.sign(txn)
    tx = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

    logger.info(
        f'ETH transfer {wallet.address} => {account}, {amount} wei,'
        f'tx: {web3.toHex(tx)}'
    )
    return tx
