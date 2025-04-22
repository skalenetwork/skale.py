import importlib
import os
from datetime import datetime

import pytest
from freezegun import freeze_time

from web3.exceptions import StaleBlockchain

import skale.config as config


@pytest.fixture
def last_block_file():
    filepath = 'last-block-file'
    os.environ['LAST_BLOCK_FILE'] = filepath
    importlib.reload(config)
    try:
        yield filepath
    finally:
        if os.path.isfile(filepath):
            os.remove(filepath)
            os.environ.pop('LAST_BLOCK_FILE')
        importlib.reload(config)


def test_call_with_outdated_client(skale):
    # because of skipTime in preparation
    current_ts = skale.web3.eth.get_block('latest')['timestamp']
    allowed_diff = config.ALLOWED_TS_DIFF
    dt = datetime.utcfromtimestamp(current_ts + allowed_diff)
    with freeze_time(dt):
        skale.validator_service.ls()
    print(current_ts, allowed_diff)
    dt = datetime.utcfromtimestamp(current_ts + allowed_diff + 5)
    with freeze_time(dt):
        with pytest.raises(StaleBlockchain):
            skale.validator_service.ls()


def test_transaction_with_outdated_client(skale):
    # because of skipTime in preparation
    current_ts = skale.web3.eth.get_block('latest')['timestamp']
    allowed_diff = config.ALLOWED_TS_DIFF

    dt = datetime.utcfromtimestamp(current_ts + allowed_diff)
    new_rotation_delay = 100
    with freeze_time(dt):
        skale.constants_holder.set_rotation_delay(new_rotation_delay, wait_for=True)

    dt = datetime.utcfromtimestamp(current_ts + allowed_diff + 15)
    new_rotation_delay = 101
    with freeze_time(dt):
        with pytest.raises(StaleBlockchain):
            skale.constants_holder.set_rotation_delay(new_rotation_delay, wait_for=True)
