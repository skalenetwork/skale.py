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
import os
import time
from typing import Iterable
from urllib.parse import urlparse

from eth_keys import keys
from web3 import Web3, WebsocketProvider, HTTPProvider
from web3.exceptions import TransactionNotFound
from web3.middleware import (
    attrdict_middleware,
    geth_poa_middleware,
    http_retry_request_middleware
)

import skale.config as config
from skale.transactions.exceptions import TransactionFailedError
from skale.utils.constants import GAS_PRICE_COEFFICIENT
from skale.utils.helper import is_test_env
from skale.transactions.exceptions import TransactionNotMinedError


logger = logging.getLogger(__name__)


WS_MAX_MESSAGE_DATA_BYTES = 5 * 1024 * 1024
MAX_WAITING_TIME = 3 * 60 * 60  # 3 hours
BLOCK_WAITING_TIMEOUT = 1
DEFAULT_HTTP_TIMEOUT = 120
DEFAULT_BLOCKS_TO_WAIT = 50


def get_provider(endpoint, timeout=DEFAULT_HTTP_TIMEOUT, request_kwargs={}):
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


class EthClientOutdatedError(Exception):
    pass


def get_last_known_block_number(state_path: str) -> int:
    if not os.path.isfile(state_path):
        return 0
    with open(state_path) as last_block_file:
        return int(last_block_file.read())


def save_last_known_block_number(state_path: str, block_number: int) -> None:
    with open(state_path, 'w') as last_block_file:
        last_block_file.write(str(block_number))


def outdated_client_time_msg(method, current_time, latest_block_timestamp, allowed_ts_diff):
    return f'{method} failed; \
current_time: {current_time}, latest_block_timestamp: {latest_block_timestamp}, \
allowed_ts_diff: {allowed_ts_diff}'


def outdated_client_file_msg(method, latest_block_number, saved_number, state_path):
    return f'{method} failed: latest_block_number: {latest_block_number}, \
        saved_number: {saved_number}, state_path: {state_path}'


def make_client_checking_middleware(allowed_ts_diff: int,
                                    state_path: str = None):
    def eth_client_checking_middleware(make_request, web3):
        def middleware(method, params):
            if method in ('eth_blockNumber', 'eth_getBlockByNumber'):
                response = make_request(method, params)
            else:
                latest_block = web3.eth.get_block('latest')
                current_time = time.time()

                ts_diff = current_time - latest_block['timestamp']
                if not is_test_env():
                    ts_diff = abs(ts_diff)

                if ts_diff > allowed_ts_diff:
                    raise EthClientOutdatedError(outdated_client_time_msg(
                        method,
                        current_time,
                        latest_block['timestamp'],
                        allowed_ts_diff
                    ))

                if state_path:
                    saved_number = get_last_known_block_number(state_path)
                    if latest_block['number'] < saved_number:
                        raise EthClientOutdatedError(outdated_client_file_msg(
                            method,
                            latest_block['number'],
                            saved_number,
                            state_path
                        ))
                    save_last_known_block_number(state_path,
                                                 latest_block['number'])
                response = make_request(method, params)
            return response
        return middleware
    return eth_client_checking_middleware


def init_web3(endpoint: str,
              provider_timeout: int = DEFAULT_HTTP_TIMEOUT,
              middlewares: Iterable = None,
              state_path: str = None, ts_diff: int = None):
    if not middlewares:
        ts_diff = ts_diff or config.ALLOWED_TS_DIFF
        state_path = state_path or config.LAST_BLOCK_FILE
        if not ts_diff == config.NO_SYNC_TS_DIFF:
            sync_middleware = make_client_checking_middleware(ts_diff, state_path)
            middewares = (
                http_retry_request_middleware,
                sync_middleware,
                attrdict_middleware
            )
        else:
            middewares = (
                http_retry_request_middleware,
                attrdict_middleware
            )

    provider = get_provider(endpoint, timeout=provider_timeout)
    web3 = Web3(provider)
    # required for rinkeby
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    for middleware in middewares:
        web3.middleware_onion.add(middleware)  # todo: may cause issues
    return web3


def get_receipt(web3, tx):
    return web3.eth.get_transaction_receipt(tx)


def get_eth_nonce(web3, address):
    return web3.eth.get_transaction_count(address)


def wait_for_receipt_by_blocks(
    web3,
    tx,
    blocks_to_wait=DEFAULT_BLOCKS_TO_WAIT,
    timeout=MAX_WAITING_TIME
):
    blocks_to_wait = blocks_to_wait or DEFAULT_BLOCKS_TO_WAIT
    timeout = timeout or MAX_WAITING_TIME
    previous_block = web3.eth.blockNumber
    current_block = previous_block
    wait_start_time = time.time()
    while time.time() - wait_start_time < timeout and \
            current_block <= previous_block + blocks_to_wait:
        try:
            receipt = get_receipt(web3, tx)
        except TransactionNotFound:
            receipt = None
        if receipt is not None:
            return receipt
        current_block = web3.eth.blockNumber
        time.sleep(3)
    raise TransactionNotMinedError(
        f'Transaction with hash: {tx} not found in {blocks_to_wait} blocks.'
    )


def wait_receipt(web3, tx, retries=30, timeout=5):
    for _ in range(0, retries):
        try:
            receipt = get_receipt(web3, tx)
        except TransactionNotFound:
            receipt = None
        if receipt is not None:
            return receipt
        time.sleep(timeout)  # pragma: no cover
    raise TransactionNotMinedError(
        f'Transaction with hash: {tx} not mined after {retries} retries.'
    )


def check_receipt(receipt, raise_error=True):
    if receipt['status'] != 1:  # pragma: no cover
        if raise_error:
            raise TransactionFailedError(
                f'Transaction failed, see receipt {receipt}'
            )
        else:
            return False
    return True


def wait_for_confirmation_blocks(
    web3,
    blocks_to_wait,
    timeout=MAX_WAITING_TIME,
    request_timeout=5
):
    current_block = start_block = web3.eth.blockNumber
    logger.info(
        f'Current block number is {current_block}, '
        f'waiting for {blocks_to_wait} confimration blocks to be mined'
    )
    wait_start_time = time.time()
    while time.time() - wait_start_time < timeout and \
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


def default_gas_price(web3: Web3) -> int:
    return web3.eth.gas_price * GAS_PRICE_COEFFICIENT
