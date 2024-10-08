from unittest import mock
import pytest
from hexbytes import HexBytes
from skale.wallets.sgx_wallet import (SgxWallet, TransactionNotSentError,
                                      TransactionNotSignedError, MessageNotSignedError)
from skale.utils.web3_utils import (
    init_web3,
    private_key_to_address,
    private_key_to_public,
    to_checksum_address
)

from tests.constants import ENDPOINT, ETH_PRIVATE_KEY, TEST_SGX_ENDPOINT
from tests.wallets.utils import BadSgxClient, SgxClient

ADDRESS = to_checksum_address(
    private_key_to_address(ETH_PRIVATE_KEY)
)


@pytest.fixture
def web3():
    return init_web3(ENDPOINT)


@pytest.fixture
@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=SgxClient)
def wallet(web3):
    return SgxWallet(TEST_SGX_ENDPOINT, web3)


def test_sgx_sign(wallet):
    tx_dict = {
        'to': '0x1057dc7277a319927D3eB43e05680B75a00eb5f4',
        'value': 9,
        'gas': 200000,
        'gasPrice': 1,
        'nonce': 7,
        'chainId': None,
        'data': b'\x9b\xd9\xbb\xc6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x95qY\xc4i\xfc;\xba\xa8\xe3\x9e\xe0\xa3$\xc28\x8a\xd6Q\xe5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\xe0\xb6\xb3\xa7d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa8\xc0\x04/Rglamorous-kitalpha\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa
    }
    wallet.sign(tx_dict)


def test_sgx_sign_and_send_without_nonce(wallet):
    send_tx_mock = mock.Mock()
    send_tx_mock.return_value = HexBytes('')
    wallet._web3.eth.send_raw_transaction = send_tx_mock
    wallet._web3.eth.get_transaction_count = mock.Mock(return_value=0)
    tx_dict = {
        'to': '0x1057dc7277a31',
        'value': 9,
        'gas': 200000,
        'gasPrice': 1,
        'chainId': None,
        'data': b'\x9b\xd9\xbb\xc6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x95qY\xc4i\xfc;\xba\xa8\xe3\x9e\xe0\xa3$\xc28\x8a\xd6Q\xe5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\xe0\xb6\xb3\xa7d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa8\xc0\x04/Rglamorous-kitalpha\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa
    }
    signed = wallet.sign(tx_dict)
    wallet.sign_and_send(tx_dict)
    send_tx_mock.assert_called_with(signed.rawTransaction)


@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=SgxClient)
def test_sgx_sign_with_key(web3):
    wallet = SgxWallet(TEST_SGX_ENDPOINT, web3, key_name='TEST_KEY')
    tx_dict = {
        'to': '0x1057dc7277a319',
        'value': 10,
        'gas': 200000,
        'gasPrice': 1,
        'nonce': 7,
        'chainId': None,
        'data': b'\x9b\xd9\xbb\xc6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x95qY\xc4i\xfc;\xba\xa8\xe3\x9e\xe0\xa3$\xc28\x8a\xd6Q\xe5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\xe0\xb6\xb3\xa7d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa8\xc0\x04/Rglamorous-kitalpha\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa
    }
    wallet.sign(tx_dict)


@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=SgxClient)
def test_sgx_sign_hash(web3):
    wallet = SgxWallet(TEST_SGX_ENDPOINT, web3, key_name='TEST_KEY')
    unsigned_hash = '0x31323331'
    signed_message = wallet.sign_hash(unsigned_hash)
    assert signed_message.signature == HexBytes('0x6161616161613131313131')


@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=SgxClient)
def test_sgx_key_init(web3):
    wallet = SgxWallet(TEST_SGX_ENDPOINT, web3, 'TEST_KEY')
    pk = private_key_to_public(ETH_PRIVATE_KEY)
    assert wallet.key_name == 'TEST_KEY'
    assert wallet.address == ADDRESS
    assert wallet.public_key == pk


@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=SgxClient)
def test_not_sent_error(web3):
    wallet = SgxWallet(TEST_SGX_ENDPOINT, web3, 'TEST_KEY')
    tx_dict = {
        'to': '0x1057dc7277a319927D3eB43e05680B75a00eb5f4',
        'value': 9,
        'gas': 200000,
        'gasPrice': 1,
        'nonce': 1,  # nonce too low
        'chainId': None,
        'data': b'\x9b\xd9\xbb\xc6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x95qY\xc4i\xfc;\xba\xa8\xe3\x9e\xe0\xa3$\xc28\x8a\xd6Q\xe5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\xe0\xb6\xb3\xa7d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa8\xc0\x04/Rglamorous-kitalpha\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa
    }

    with pytest.raises(TransactionNotSentError):
        wallet.sign_and_send(tx_dict)


@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=BadSgxClient)
def test_sign_error(web3):
    wallet = SgxWallet(TEST_SGX_ENDPOINT, web3, 'TEST_KEY')
    tx_dict = {
        'to': '0x1057dc7277a319927D3eB43e05680B75a00eb5f4',
        'value': 9,
        'gas': 200000,
        'gasPrice': 1,
        'nonce': 7,
        'chainId': None,
        'data': b'\x9b\xd9\xbb\xc6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x95qY\xc4i\xfc;\xba\xa8\xe3\x9e\xe0\xa3$\xc28\x8a\xd6Q\xe5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\xe0\xb6\xb3\xa7d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa8\xc0\x04/Rglamorous-kitalpha\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa
    }
    with pytest.raises(TransactionNotSignedError):
        wallet.sign(tx_dict)


@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=BadSgxClient)
def test_sign_hash_error(web3):
    wallet = SgxWallet(TEST_SGX_ENDPOINT, web3, 'TEST_KEY')
    with pytest.raises(MessageNotSignedError):
        wallet.sign_hash('0x')
