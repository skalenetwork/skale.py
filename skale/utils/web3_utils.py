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
import time
from urllib.parse import urlparse

from eth_keys import keys
from web3 import Web3, WebsocketProvider, HTTPProvider
from web3.exceptions import TransactionNotFound

logger = logging.getLogger(__name__)


WS_MAX_MESSAGE_DATA_BYTES = 5 * 1024 * 1024
MAX_WAITING_TIME = 1200


def get_provider(endpoint, timeout=10, request_kwargs={}):
    scheme = urlparse(endpoint).scheme
    if scheme == 'ws' or scheme == 'wss':
        kwargs = request_kwargs or {'max_size': WS_MAX_MESSAGE_DATA_BYTES}
        return WebsocketProvider(endpoint, websocket_timeout=timeout,
                                 websocket_kwargs=kwargs)

    if scheme == 'http' or scheme == 'https':
        kwargs = {'timeout': timeout, **request_kwargs}
        return HTTPProvider(endpoint, request_kwargs=kwargs)

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


def wait_for_receipt_by_blocks(web3, tx, timeout=4, blocks_to_wait=50):
    previous_block = web3.eth.blockNumber
    current_block = previous_block
    wait_start_time = time.time()
    while time.time() - wait_start_time < MAX_WAITING_TIME and \
            current_block <= previous_block + blocks_to_wait:
        try:
            receipt = get_receipt(web3, tx)
        except TransactionNotFound:
            receipt = None
        if receipt is not None:
            return receipt
        current_block = web3.eth.blockNumber
        time.sleep(timeout)
    raise TransactionNotFound(f"Transaction with hash: {tx} not found.")


def wait_receipt(web3, tx, retries=30, timeout=5):
    for _ in range(0, retries):
        try:
            receipt = get_receipt(web3, tx)
        except TransactionNotFound:
            receipt = None
        if receipt is not None:
            return receipt
        time.sleep(timeout)  # pragma: no cover
    raise TransactionNotFound(f"Transaction with hash: {tx} not found.")


def check_receipt(receipt, raise_error=True):
    if receipt['status'] != 1:  # pragma: no cover
        if raise_error:
            raise ValueError("Transaction failed, see receipt", receipt)
        else:
            return False
    return True


def wait_for_confirmation_blocks(web3, blocks_to_wait, request_timeout=5):
    current_block = start_block = web3.eth.blockNumber
    logger.info(
        f'Current block number is {current_block}, '
        f'waiting for {blocks_to_wait} confimration blocks to be mined'
    )
    wait_start_time = time.time()
    while time.time() - wait_start_time < MAX_WAITING_TIME and \
            current_block <= start_block + blocks_to_wait:
        current_block = web3.eth.blockNumber
        time.sleep(request_timeout)


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
