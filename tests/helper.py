""" SKALE test utilities """

from contextlib import contextmanager
from timeit import default_timer as timer

from unittest.mock import Mock, MagicMock
from web3 import Web3

from skale import SkaleManager, SkaleAllocator
from skale.utils.helper import get_abi
from skale.wallets import Web3Wallet
from tests.constants import (ENDPOINT, TEST_ABI_FILEPATH,
                             TEST_ALLOCATOR_ABI_FILEPATH,
                             ETH_PRIVATE_KEY)


def response_mock(status_code=0, json_data=None, cookies=None,
                  headers=None, raw=None):
    result = MagicMock()
    result.status_code = status_code
    result.json = MagicMock(return_value=json_data)
    result.cookies = cookies
    result.headers = headers
    result.raw = raw
    return result


def request_mock(response_mock):
    return Mock(return_value=response_mock)


def init_skale(web3: Web3,
               eth_private_key: str = ETH_PRIVATE_KEY,
               test_abi_filepath: str = TEST_ABI_FILEPATH) -> SkaleManager:
    wallet = Web3Wallet(eth_private_key, web3)
    skale_manager_address = get_abi(test_abi_filepath)['skale_manager_address']
    return SkaleManager(ENDPOINT, skale_manager_address, wallet)


def init_skale_allocator(
    web3: Web3,
    eth_private_key: str = ETH_PRIVATE_KEY,
    test_allocator_abi_filepath: str = TEST_ALLOCATOR_ABI_FILEPATH
) -> SkaleAllocator:
    wallet = Web3Wallet(eth_private_key, web3)
    allocator_address = get_abi(test_allocator_abi_filepath)['allocator_address']
    return SkaleAllocator(ENDPOINT, allocator_address, wallet)


@contextmanager
def in_time(seconds):
    start_ts = timer()
    yield
    ts_diff = timer() - start_ts
    assert ts_diff < seconds, (ts_diff, seconds)
