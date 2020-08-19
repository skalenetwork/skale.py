""" SKALE config test """

import pytest
from web3.auto import w3

from skale import SkaleManager, SkaleAllocator
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3

from tests.constants import (ENDPOINT, TEST_ABI_FILEPATH, TEST_ALLOCATOR_ABI_FILEPATH,
                             ETH_PRIVATE_KEY)


@pytest.fixture
def skale():
    '''Returns a SKALE Manager instance with provider from config'''
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    return SkaleManager(ENDPOINT, TEST_ABI_FILEPATH, wallet)


@pytest.fixture
def skale_allocator():
    '''Returns a SKALE Allocator instance with provider from config'''
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    return SkaleAllocator(ENDPOINT, TEST_ALLOCATOR_ABI_FILEPATH, wallet)


@pytest.fixture
def empty_account():
    return w3.eth.account.create()
