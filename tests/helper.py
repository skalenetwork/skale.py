"""SKALE test utilities"""

from contextlib import contextmanager
from timeit import default_timer as timer
from unittest.mock import MagicMock, Mock

from eth_typing import HexStr
from web3 import Web3

from skale import FairManager, SkaleAllocator, SkaleManager
from skale.utils.helper import get_allocator_address, get_skale_manager_address
from skale.wallets import Web3Wallet
from tests.constants import (
    ENDPOINT,
    ETH_PRIVATE_KEY,
    FAIR_CONTRACTS,
    TEST_ABI_FILEPATH,
    TEST_ALLOCATOR_ABI_FILEPATH,
)


def response_mock(status_code=0, json_data=None, cookies=None, headers=None, raw=None):
    result = MagicMock()
    result.status_code = status_code
    result.json = MagicMock(return_value=json_data)
    result.cookies = cookies
    result.headers = headers
    result.raw = raw
    return result


def request_mock(response_mock):
    return Mock(return_value=response_mock)


def init_skale(
    web3: Web3,
    eth_private_key: HexStr = ETH_PRIVATE_KEY,
    test_abi_filepath: str = TEST_ABI_FILEPATH,
) -> SkaleManager:
    wallet = Web3Wallet(eth_private_key, web3)
    return SkaleManager(ENDPOINT, get_skale_manager_address(test_abi_filepath), wallet)


def init_fair(web3: Web3, eth_private_key: HexStr = ETH_PRIVATE_KEY) -> FairManager:
    wallet = Web3Wallet(eth_private_key, web3)
    if not FAIR_CONTRACTS:
        raise ValueError('FAIR_CONTRACTS is not set')
    return FairManager(ENDPOINT, FAIR_CONTRACTS, wallet)


def init_skale_allocator(
    web3: Web3,
    eth_private_key: HexStr = ETH_PRIVATE_KEY,
    test_allocator_abi_filepath: str = TEST_ALLOCATOR_ABI_FILEPATH,
) -> SkaleAllocator:
    wallet = Web3Wallet(eth_private_key, web3)
    return SkaleAllocator(ENDPOINT, get_allocator_address(test_allocator_abi_filepath), wallet)


@contextmanager
def in_time(seconds):
    start_ts = timer()
    yield
    ts_diff = timer() - start_ts
    assert ts_diff < seconds, (ts_diff, seconds)
