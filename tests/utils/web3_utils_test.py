import importlib
import os

import pytest

import skale.config as config
from skale.utils.web3_utils import (
    BlockWaitingTimeoutError,
    get_last_knowing_block,
    save_last_knowing_block,
    wait_until_block
)


def test_wait_until_block(web3):
    current_block = web3.eth.blockNumber
    needed_block = current_block + 1
    wait_until_block(web3, needed_block)
    assert web3.eth.blockNumber >= needed_block


def test_wait_until_block_failed(web3):
    current_block = web3.eth.blockNumber
    needed_block = current_block + 10
    with pytest.raises(BlockWaitingTimeoutError):
        wait_until_block(web3, needed_block, max_waiting_time=1)


@pytest.fixture
def last_block_file():
    filename = 'last-block-file'
    os.environ['LAST_BLOCK_FILE'] = filename
    importlib.reload(config)
    yield
    if os.path.isfile(filename):
        os.remove(filename)
    os.environ.pop('LAST_BLOCK_FILE')
    importlib.reload(config)


def test_default_get_last_knowing_block():
    assert get_last_knowing_block() == 0


def test_get_save_last_knowing_block(last_block_file):
    last_block = 15
    save_last_knowing_block(last_block)
    assert get_last_knowing_block() == last_block


def test_rpc_call_with_call(skale, last_block_file):
    current_block = skale.web3.eth.blockNumber
    needed_block = current_block + 10
    save_last_knowing_block(needed_block)
    skale.validator_service.ls()
    assert skale.web3.eth.blockNumber >= needed_block
