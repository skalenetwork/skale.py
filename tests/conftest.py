""" SKALE config test """

import mock
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


@pytest.fixture
def patched_wallet_failed_tx_skale(skale):
    tmp_wait_for_receipt = skale.wallet.wait_for_receipt
    skale.wallet.wait_for_receipt = mock.Mock(
        return_value=('txHash', {'status': 0})
    )
    yield skale
    skale.wallet.wait_for_receipt = tmp_wait_for_receipt
