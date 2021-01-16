import importlib
import os
from datetime import datetime

import pytest
from freezegun import freeze_time

import skale.config as config
from skale.utils.web3_utils import (
    EthClientOutdatedError,
    get_last_knowing_block_number,
    save_last_knowing_block_number
)


@pytest.fixture
def last_block_file():
    filepath = 'last-block-file'
    os.environ['LAST_BLOCK_FILE'] = filepath
    importlib.reload(config)
    yield filepath
    if os.path.isfile(filepath):
        os.remove(filepath)
    os.environ.pop('LAST_BLOCK_FILE')
    importlib.reload(config)


def test_default_get_last_knowing_block_number():
    assert get_last_knowing_block_number('') == 0


def test_get_save_last_knowing_block_number(last_block_file):
    state_path = last_block_file
    last_block = 15
    save_last_knowing_block_number(state_path, last_block)
    assert get_last_knowing_block_number(state_path) == last_block


def test_call_with_last_block_file(last_block_file, skale):
    state_path = last_block_file
    current_block = skale.web3.eth.blockNumber
    needed_block = current_block
    save_last_knowing_block_number(state_path, needed_block)
    skale.validator_service.ls()

    current_block = skale.web3.eth.blockNumber
    needed_block = current_block + 10
    save_last_knowing_block_number(state_path, needed_block)
    with pytest.raises(EthClientOutdatedError):
        skale.validator_service.ls()
    assert get_last_knowing_block_number(state_path) >= needed_block


def test_call_with_outdated_client(skale):
    # because of skipTime in preparation
    current_ts = skale.web3.eth.getBlock('latest')['timestamp']
    allowed_diff = config.ALLOWED_TS_DIFF
    dt = datetime.utcfromtimestamp(current_ts + allowed_diff)
    with freeze_time(dt):
        skale.validator_service.ls()
    dt = datetime.utcfromtimestamp(current_ts + allowed_diff + 4)
    with freeze_time(dt):
        with pytest.raises(EthClientOutdatedError):
            skale.validator_service.ls()


def test_transaction_with_last_block_file(last_block_file, skale):
    state_path = last_block_file
    current_block = skale.web3.eth.blockNumber
    needed_block = current_block
    save_last_knowing_block_number(state_path, needed_block)

    new_rotation_delay = 100
    skale.constants_holder.set_rotation_delay(new_rotation_delay,
                                              wait_for=True)

    current_block = skale.web3.eth.blockNumber
    last_block = current_block + 5
    save_last_knowing_block_number(state_path, last_block)
    new_rotation_delay = 101
    with pytest.raises(EthClientOutdatedError):
        skale.constants_holder.set_rotation_delay(
            new_rotation_delay,
            wait_for=True
        )


def test_transaction_with_outdated_client(skale):
    # because of skipTime in preparation
    current_ts = skale.web3.eth.getBlock('latest')['timestamp']
    allowed_diff = config.ALLOWED_TS_DIFF

    dt = datetime.utcfromtimestamp(current_ts + allowed_diff)
    new_rotation_delay = 100
    with freeze_time(dt):
        skale.constants_holder.set_rotation_delay(
            new_rotation_delay, wait_for=True)

    dt = datetime.utcfromtimestamp(current_ts + allowed_diff + 5)
    new_rotation_delay = 101
    with freeze_time(dt):
        with pytest.raises(EthClientOutdatedError):
            skale.constants_holder.set_rotation_delay(
                new_rotation_delay,
                wait_for=True
            )
