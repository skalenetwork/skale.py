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

import time
import logging
from typing import Any, Dict, Iterable
from urllib.parse import urlparse

from eth_keys.main import lazy_key_api as keys
from eth_typing import Address, AnyAddress, ChecksumAddress, HexStr
from web3 import Web3, LegacyWebSocketProvider, HTTPProvider
from web3.exceptions import TransactionNotFound, ProviderConnectionError
from web3.middleware import AttributeDictMiddleware, Middleware, StalecheckMiddlewareBuilder
from web3.providers.base import JSONBaseProvider
from web3.types import _Hash32, ENS, Nonce, TxReceipt

import skale.config as config
from skale.transactions.exceptions import TransactionFailedError
from skale.utils.constants import GAS_PRICE_COEFFICIENT
from skale.transactions.exceptions import TransactionNotMinedError


logger = logging.getLogger(__name__)


WS_MAX_MESSAGE_DATA_BYTES = 5 * 1024 * 1024
MAX_WAITING_TIME = 3 * 60 * 60  # 3 hours
BLOCK_WAITING_TIMEOUT = 1
DEFAULT_HTTP_TIMEOUT = 120
DEFAULT_BLOCKS_TO_WAIT = 50


def get_provider(
    endpoint: str, timeout: int = DEFAULT_HTTP_TIMEOUT, request_kwargs: Dict[str, Any] | None = None
) -> JSONBaseProvider:
    scheme = urlparse(endpoint).scheme
    if scheme == 'ws' or scheme == 'wss':
        kwargs = request_kwargs or {'max_size': WS_MAX_MESSAGE_DATA_BYTES}
        return LegacyWebSocketProvider(endpoint, websocket_timeout=timeout, websocket_kwargs=kwargs)

    if scheme == 'http' or scheme == 'https':
        kwargs = {'timeout': timeout, **(request_kwargs or {})}
        return HTTPProvider(endpoint, request_kwargs=kwargs)

    raise Exception('Wrong endpoint option.Supported endpoint schemes: http/https/ws/wss')


def init_web3(
    endpoint: str,
    provider_timeout: int = DEFAULT_HTTP_TIMEOUT,
    middlewares: Iterable[Middleware] | None = None,
    ts_diff: int | None = None,
) -> Web3:
    provider = get_provider(endpoint, timeout=provider_timeout)
    w3 = Web3(provider)
    if not middlewares:
        ts_diff = ts_diff or config.ALLOWED_TS_DIFF
        if not ts_diff == config.NO_SYNC_TS_DIFF:
            stalecheck_middleware = StalecheckMiddlewareBuilder.build(config.ALLOWED_TS_DIFF)
            middlewares = [stalecheck_middleware, AttributeDictMiddleware]
        else:
            middlewares = [AttributeDictMiddleware]
    for middleware in middlewares:
        w3.middleware_onion.add(middleware)
    return w3


def get_endpoint(endpoint: str | list[str]) -> str:
    if isinstance(endpoint, str):
        return endpoint
    elif isinstance(endpoint, list) and len(endpoint) > 0:
        return _get_connected_endpoint(endpoint)
    else:
        raise ValueError('Endpoint must be a string or a non-empty list of strings.')


def _get_connected_endpoint(endpoints: list[str]) -> str:
    for url in endpoints:
        try:
            w3 = Web3(HTTPProvider(url))
            if w3.is_connected():
                return url
        except ProviderConnectionError as e:
            logger.warning(f'Could not connect to {url}. Error: {e}. Trying next endpoint...')
            time.sleep(2)
    raise ProviderConnectionError(f'Could not connect to any RPC endpoints: {endpoints}')


def get_receipt(web3: Web3, tx: _Hash32) -> TxReceipt:
    return web3.eth.get_transaction_receipt(tx)


def get_eth_nonce(web3: Web3, address: Address | ChecksumAddress | ENS) -> Nonce:
    return web3.eth.get_transaction_count(address)


def wait_for_receipt_by_blocks(
    web3: Web3,
    tx: _Hash32,
    blocks_to_wait: int = DEFAULT_BLOCKS_TO_WAIT,
    timeout: int = MAX_WAITING_TIME,
) -> TxReceipt:
    blocks_to_wait = blocks_to_wait or DEFAULT_BLOCKS_TO_WAIT
    timeout = timeout or MAX_WAITING_TIME
    previous_block = web3.eth.block_number
    current_block = previous_block
    wait_start_time = time.time()
    while (
        time.time() - wait_start_time < timeout and current_block <= previous_block + blocks_to_wait
    ):
        try:
            receipt = get_receipt(web3, tx)
        except TransactionNotFound:
            receipt = None
        if receipt is not None:
            return receipt
        current_block = web3.eth.block_number
        time.sleep(3)
    raise TransactionNotMinedError(
        f'Transaction with hash: {str(tx)} not found in {blocks_to_wait} blocks.'
    )


def wait_receipt(web3: Web3, tx: _Hash32, retries: int = 30, timeout: int = 5) -> TxReceipt:
    for _ in range(0, retries):
        try:
            receipt = get_receipt(web3, tx)
        except TransactionNotFound:
            receipt = None
        if receipt is not None:
            return receipt
        time.sleep(timeout)  # pragma: no cover
    raise TransactionNotMinedError(
        f'Transaction with hash: {str(tx)} not mined after {retries} retries.'
    )


def check_receipt(receipt: TxReceipt, raise_error: bool = True) -> bool:
    if receipt['status'] != 1:  # pragma: no cover
        if raise_error:
            raise TransactionFailedError(f'Transaction failed, see receipt {receipt}')
        else:
            return False
    return True


def wait_for_confirmation_blocks(
    web3: Web3, blocks_to_wait: int, timeout: int = MAX_WAITING_TIME, request_timeout: int = 5
) -> None:
    current_block = start_block = web3.eth.block_number
    logger.info(
        f'Current block number is {current_block}, '
        f'waiting for {blocks_to_wait} confimration blocks to be mined'
    )
    wait_start_time = time.time()
    while time.time() - wait_start_time < timeout and current_block <= start_block + blocks_to_wait:
        current_block = web3.eth.block_number
        time.sleep(request_timeout)


def private_key_to_public(pr: HexStr) -> HexStr:
    pr_bytes = Web3.to_bytes(hexstr=pr)
    prk = keys.PrivateKey(pr_bytes)
    pk = prk.public_key
    return HexStr(pk.to_hex())


def public_key_to_address(pk: HexStr) -> HexStr:
    hash = Web3.keccak(hexstr=str(pk))
    return Web3.to_hex(hash[-20:])


def private_key_to_address(pr: HexStr) -> HexStr:
    pk = private_key_to_public(pr)
    return public_key_to_address(pk)


def to_checksum_address(address: AnyAddress | str | bytes) -> ChecksumAddress:
    return Web3.to_checksum_address(address)


def default_gas_price(web3: Web3) -> int:
    return web3.eth.gas_price * GAS_PRICE_COEFFICIENT
