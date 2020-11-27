""" SKALE config test """

import pytest
from web3.auto import w3

from tests.helper import init_skale, init_skale_allocator


@pytest.fixture
def skale():
    '''Returns a SKALE Manager instance with provider from config'''
    return init_skale()


@pytest.fixture
def skale_allocator():
    '''Returns a SKALE Allocator instance with provider from config'''
    return init_skale_allocator()


@pytest.fixture
def empty_account():
    return w3.eth.account.create()
