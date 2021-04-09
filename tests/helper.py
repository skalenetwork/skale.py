""" SKALE test utilities """

from mock import Mock, MagicMock
from web3 import Web3

from skale import SkaleManager, SkaleAllocator
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
    return SkaleManager(ENDPOINT, test_abi_filepath, wallet)


def init_skale_allocator(
    web3: Web3,
    eth_private_key: str = ETH_PRIVATE_KEY,
    test_allocator_abi_filepath: str = TEST_ALLOCATOR_ABI_FILEPATH
) -> SkaleAllocator:
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    return SkaleAllocator(ENDPOINT, TEST_ALLOCATOR_ABI_FILEPATH, wallet)
