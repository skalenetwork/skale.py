from datetime import datetime
from unittest import mock

import pytest
from freezegun import freeze_time

from skale.wallets.redis_wallet import (
    RedisWalletAdapter,
    RedisWalletDroppedError,
    RedisWalletEmptyStatusError,
    RedisWalletNotSentError,
    RedisWalletWaitError,
)
from tests.helper import in_time


@pytest.fixture
def rdp(skale):
    return RedisWalletAdapter(mock.Mock(), 'transactions', skale.wallet)


class RedisTestError(Exception):
    pass


def test_make_raw_id():
    tx_id = RedisWalletAdapter._make_raw_id()
    assert tx_id.startswith(b'tx-')
    assert len(tx_id) == 19


def test_make_score():
    cts = 1623233060
    dt = datetime.utcfromtimestamp(cts)
    with freeze_time(dt):
        score = RedisWalletAdapter._make_score(priority=5)
        assert score == 51623233060


def test_make_record():
    tx = {
        'from': '0x1',
        'to': '0x2',
        'value': 1,
        'gasPrice': 1,
        'gas': 22000,
        'nonce': 1,
        'chainId': 1,
    }
    score = '51623233060'
    tx_id, r = RedisWalletAdapter._make_record(tx, score, 2, method='createNode')
    assert tx_id.startswith(b'tx-') and len(tx_id) == 19
    assert (
        r
        == b'{"status": "PROPOSED", "score": "51623233060", "multiplier": 2, "tx_hash": null, "method": "createNode", "from": "0x1", "to": "0x2", "value": 1, "gasPrice": 1, "gas": 22000, "nonce": 1, "chainId": 1}'
    )  # noqa


def test_sign_and_send(rdp):
    tx = {
        'from': '0x1',
        'to': '0x2',
        'value': 1,
        'gasPrice': 1,
        'gas': 22000,
        'nonce': 1,
        'chainId': 1,
    }
    tx_id = rdp.sign_and_send(tx, multiplier=2, priority=5)
    assert str(tx_id).startswith('tx-') and len(tx_id) == 19

    rdp.rs.pipeline = mock.Mock(side_effect=RedisTestError('rtest'))
    with pytest.raises(RedisWalletNotSentError):
        tx_id = rdp.sign_and_send(tx, multiplier=2, priority=5)


def test_rdp_wait(rdp):
    tx_id = 'tx-tttttttttttttttt'
    rdp.get_record = mock.Mock(return_value=None)
    with in_time(3):
        with pytest.raises(RedisWalletEmptyStatusError):
            rdp.wait(tx_id, timeout=2)

    rdp.get_record = mock.Mock(return_value={'tx_hash': 'test', 'status': 'DROPPED'})
    with in_time(2):
        with pytest.raises(RedisWalletDroppedError):
            rdp.wait(tx_id, timeout=100)

    rdp.get_record = mock.Mock(side_effect=RedisTestError('test'))
    with in_time(2):
        with pytest.raises(RedisWalletWaitError):
            rdp.wait(tx_id, timeout=100)

    rdp.get_record = mock.Mock(return_value={'tx_hash': 'test', 'status': 'SUCCESS'})
    fake_receipt = {'test': 'test'}
    with mock.patch('skale.wallets.redis_wallet.get_receipt', return_value=fake_receipt):
        with in_time(2):
            assert rdp.wait(tx_id, timeout=100) == fake_receipt
