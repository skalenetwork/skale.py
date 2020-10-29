import mock
import pytest

from hexbytes import HexBytes
from skale.utils.web3_utils import (
    init_web3,
    private_key_to_address,
    private_key_to_public,
    to_checksum_address
)
from skale.wallets import SgxQueueWallet
from skale.wallets.sgx_queue_wallet import (
    QueueTxFailedError,
    QueueTxNotFoundError,
    QueueTxNotSentError
)
from tests.constants import (
    ENDPOINT,
    ETH_PRIVATE_KEY,
    TEST_REDIS_URL,
    TEST_SGX_SERVER_URL
)
from tests.wallets.utils import RedisClientMock, SgxClientMock


DEFAULT_CHANNEL_NAME = 'test'


def init_sgx_queue_wallet(
    channel: str = DEFAULT_CHANNEL_NAME
) -> SgxQueueWallet:
    web3 = init_web3(ENDPOINT)
    channel = 'test'
    return SgxQueueWallet(
        TEST_SGX_SERVER_URL,
        web3,
        channel=channel,
        redis_url=TEST_REDIS_URL
    )


@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=SgxClientMock)
def test_address_public_key():
    wallet = init_sgx_queue_wallet(DEFAULT_CHANNEL_NAME)
    assert wallet.address == to_checksum_address(
        private_key_to_address(ETH_PRIVATE_KEY))
    assert wallet.public_key == private_key_to_public(ETH_PRIVATE_KEY)


@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=SgxClientMock)
def test_sgx_sign(skale):
    wallet = init_sgx_queue_wallet(DEFAULT_CHANNEL_NAME)
    tx_dict = {
        'to': skale.wallet.address,
        'value': 9,
        'gas': 200000,
        'gasPrice': 1,
        'nonce': 7,
        'chainId': None,
        'data': b'\x9b\xd9\xbb\xc6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x95qY\xc4i\xfc;\xba\xa8\xe3\x9e\xe0\xa3$\xc28\x8a\xd6Q\xe5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\xe0\xb6\xb3\xa7d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa8\xc0\x04/Rglamorous-kitalpha\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa
    }
    signature = wallet.sign(tx_dict)
    assert signature == {
        'rawTransaction': HexBytes('0x000000000000'),
        'hash': HexBytes('0x000000000000'),
        'r': 100000000000,
        's': 100000000000,
        'v': 37,
    }


def compose_tx(skale):
    amount = 0.1
    gas_price = skale.gas_price
    address = skale.wallet.address
    return {
        'to': address,
        'value': amount,
        'gasPrice': gas_price,
        'gas': 22000
    }


@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=SgxClientMock)
def test_sgx_queue_wallet_tx_success(skale):
    RedisClientMock.response_message = {
        'type': 'message',
        'pattern': None,
        'channel': b'tx.receipt.test',
        'data': b'{"channel": "test", "status": "ok", "payload": {"tx_hash": "0xb33f00eafd818127624d09030aeb2a7ff52835c3200ad2ffec140868422c95df", "receipt": {"transactionHash": "0xb76af437bdef07c37fc54316b711887b52442d94527f796c42c583a3b8e26525", "transactionIndex": 0, "blockHash": "0x81e9558ec8ae78c461a8face1232360777c9857a7335bb3dff9b7be2276a4754", "blockNumber": 27734, "from": "0x8BD86c4515A4DB2723706AFe94E024a34e630ED8", "to": "0x8BD86c4515A4DB2723706AFe94E024a34e630ED8", "gasUsed": 21000, "cumulativeGasUsed": 21000, "contractAddress": null, "logs": [], "status": 1, "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"}}}'  # noqa
    }
    with mock.patch('skale.wallets.sgx_queue_wallet.Redis', RedisClientMock):
        wallet = init_sgx_queue_wallet()
        tx_hash, receipt = wallet.wait_for_receipt(compose_tx(skale))
        assert tx_hash
        assert receipt['status'] == 1


@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=SgxClientMock)
def test_sgx_queue_wallet_tx_not_sent(skale):
    RedisClientMock.response_message = {
        'type': 'message', 'pattern': None, 'channel': b'tx.receipt.test', 'data': b'{"channel": "test", "status": "error", "payload": {"type": "not-sent", "tx_hash": null, "msg": "Serialization failed because of field value (\\"Cannot serialize negative integers\\")", "receipt": null}}'  # noqa
    }
    with mock.patch('skale.wallets.sgx_queue_wallet.Redis', RedisClientMock):
        wallet = init_sgx_queue_wallet()
        with pytest.raises(QueueTxNotSentError):
            wallet.wait_for_receipt(compose_tx(skale))


@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=SgxClientMock)
def test_sgx_queue_wallet_tx_not_found(skale):
    RedisClientMock.response_message = {
        'type': 'message', 'pattern': None, 'channel': b'tx.receipt.test', 'data': b'{"channel": "test", "status": "error", "payload": {"type": "not-found", "tx_hash": null, "msg": "Not found", "receipt": null}}'  # noqa
    }
    with mock.patch('skale.wallets.sgx_queue_wallet.Redis', RedisClientMock):
        wallet = init_sgx_queue_wallet()
        with pytest.raises(QueueTxNotFoundError):
            wallet.wait_for_receipt(compose_tx(skale))


@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=SgxClientMock)
def test_sgx_queue_wallet_tx_failed(skale):
    RedisClientMock.response_message = {
        'type': 'message', 'pattern': None, 'channel': b'tx.receipt.test', 'data': b'{"channel": "test", "status": "error", "payload": {"type": "tx-failed", "tx_hash": null, "msg": "Not found", "receipt": null}}'  # noqa
    }
    with mock.patch('skale.wallets.sgx_queue_wallet.Redis', RedisClientMock):
        wallet = init_sgx_queue_wallet()
        with pytest.raises(QueueTxFailedError):
            wallet.wait_for_receipt(compose_tx(skale))


@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=SgxClientMock)
def test_sgx_queue_wallet_sign_and_send(skale):
    wallet = init_sgx_queue_wallet()
    with pytest.raises(NotImplementedError):
        wallet.sign_and_send(compose_tx(skale))
