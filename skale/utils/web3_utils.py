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
""" SKALE web3 utilities """

import logging
from time import sleep
from urllib.parse import urlparse

from eth_keys import keys
from web3 import Web3, WebsocketProvider, HTTPProvider
from web3.exceptions import TransactionNotFound

logger = logging.getLogger(__name__)


def get_provider(endpoint):
    scheme = urlparse(endpoint).scheme
    if scheme == 'ws' or scheme == 'wss':
        return WebsocketProvider(endpoint)
    if scheme == 'http' or scheme == 'https':
        return HTTPProvider(endpoint)
    raise Exception(
        'Wrong endpoint option.'
        'Supported endpoint schemes: http/https/ws/wss'
    )


def init_web3(endpoint):
    provider = get_provider(endpoint)
    return Web3(provider)


def get_receipt(web3, tx):
    return web3.eth.getTransactionReceipt(tx)


def get_eth_nonce(web3, address):
    return web3.eth.getTransactionCount(address)


def wait_receipt(web3, tx, retries=10, timeout=5):
    for _ in range(0, retries):
        try:
            receipt = get_receipt(web3, tx)
        except TransactionNotFound:
            receipt = None
        if receipt is not None:
            return receipt
        sleep(timeout)  # pragma: no cover
    raise TransactionNotFound(f"Transaction with hash: {tx} not found.")


def check_receipt(receipt):
    if receipt['status'] != 1:  # pragma: no cover
        raise ValueError("Transaction failed, see receipt", receipt)
    return True


def private_key_to_public(pr):
    pr_bytes = Web3.toBytes(hexstr=pr)
    pk = keys.PrivateKey(pr_bytes)
    return pk.public_key


def public_key_to_address(pk):
    hash = Web3.keccak(hexstr=str(pk))
    return Web3.toHex(hash[-20:])


def private_key_to_address(pr):
    pk = private_key_to_public(pr)
    return public_key_to_address(pk)


def to_checksum_address(address):
    return Web3.toChecksumAddress(address)


def wallet_to_public_key(wallet):
    if isinstance(wallet, dict):
        return private_key_to_public(wallet['private_key'])
    else:
        return wallet['public_key']
