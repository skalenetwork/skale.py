""" SKALE config test """

import pytest
from web3.auto import w3

from skale.utils.web3_utils import init_web3

from tests.constants import (ENDPOINT)
from tests.helper import init_skale, init_skale_allocator


@pytest.fixture
def web3():
    """ Returns a SKALE Manager instance with provider from config """
    return init_web3(ENDPOINT)


@pytest.fixture
def skale(web3):
    """ Returns a SKALE Manager instance with provider from config """
    return init_skale(web3)


@pytest.fixture
def skale_allocator(web3):
    '''Returns a SKALE Allocator instance with provider from config'''
    return init_skale_allocator(web3)


@pytest.fixture
def empty_account():
    return w3.eth.account.create()
