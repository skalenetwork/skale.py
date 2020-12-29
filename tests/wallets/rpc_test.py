""" SKALE RPCWallet test """


from http import HTTPStatus

import pytest
import mock

from hexbytes import HexBytes
from eth_account.datastructures import AttributeDict
from skale.wallets import RPCWallet
from skale.utils.exceptions import RPCWalletError

from tests.constants import (
    ENDPOINT, EMPTY_HEX_STR, ETH_PRIVATE_KEY,
    NOT_EXISTING_RPC_WALLET_URL, TEST_SGX_ENDPOINT, TEST_RPC_WALLET_URL
)
from tests.helper import response_mock, request_mock
from tests.wallets.utils import SgxClient
from skale.utils.web3_utils import (
    init_web3, private_key_to_address, to_checksum_address
)


TX_DICT = {
    'to': '0x1057dc7277a319927D3eB43e05680B75a00eb5f4',
    'value': 9,
    'gas': 200000,
    'gasPrice': 1,
    'nonce': 7,
    'chainId': None,
    'data': '0x0'
}

ADDRESS = to_checksum_address(
    private_key_to_address(ETH_PRIVATE_KEY)
)
EMPTY_ETH_ACCOUNT = '0x0000000000000000000000000000000000000000'
TEST_MAX_RETRIES = 3


@pytest.fixture
def web3():
    return init_web3(ENDPOINT)


@pytest.fixture
@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=SgxClient)
def wallet(web3):
    return RPCWallet(TEST_RPC_WALLET_URL, TEST_SGX_ENDPOINT, web3,
                     retry_if_failed=True)


@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=SgxClient)
def test_rpc_not_available(web3):
    wallet = RPCWallet(NOT_EXISTING_RPC_WALLET_URL, TEST_SGX_ENDPOINT, web3)
    with pytest.raises(RPCWalletError):
        wallet.sign_and_send({})


def test_rpc_sign_and_send(wallet):
    res_mock = response_mock(HTTPStatus.OK,
                             {'data': {'transaction_hash': EMPTY_HEX_STR},
                              'error': None})
    with mock.patch('requests.post', new=request_mock(res_mock)):
        tx_hash = wallet.sign_and_send(TX_DICT)
        assert tx_hash == EMPTY_HEX_STR


def test_rpc_sign_and_send_fails(wallet):
    cnt = 0

    def post_mock(*args, **kwargs):
        nonlocal cnt
        response_mock = mock.Mock()
        if cnt < TEST_MAX_RETRIES:
            rv = {'data': None, 'error': object()}
            cnt += 1
        else:
            rv = {'data': 'test', 'error': ''}

        response_mock.json = mock.Mock(return_value=rv)
        return response_mock

    with mock.patch('requests.post', post_mock):
        with pytest.raises(RPCWalletError):
            wallet.sign_and_send(TX_DICT)

        assert cnt == TEST_MAX_RETRIES


@mock.patch('skale.wallets.sgx_wallet.SgxClient', new=SgxClient)
def test_rpc_sign_and_send_sgx_unreachable_no_retries(web3):
    res_mock = response_mock(HTTPStatus.BAD_REQUEST,
                             {'data': None,
                              'error': 'Sgx server is unreachable'})
    wallet = RPCWallet(NOT_EXISTING_RPC_WALLET_URL, TEST_SGX_ENDPOINT, web3)
    with mock.patch('requests.post', new=request_mock(res_mock)):
        with pytest.raises(RPCWalletError):
            wallet.sign_and_send(TX_DICT)
            assert res_mock.call_count == 1


def test_rpc_sign_and_send_sgx_unreachable(wallet):
    cnt = 0

    def post_mock(*args, **kwargs):
        nonlocal cnt
        response_mock = mock.Mock()
        if cnt < TEST_MAX_RETRIES:
            rv = {'data': None, 'error': 'Sgx server is unreachable'}
            cnt += 1
        else:
            rv = {'data': 'test', 'error': ''}

        response_mock.json = mock.Mock(return_value=rv)
        return response_mock

    with mock.patch('requests.post', post_mock):
        with pytest.raises(RPCWalletError):
            wallet.sign_and_send(TX_DICT)

        assert cnt == TEST_MAX_RETRIES


def test_sign(wallet):
    signed_data = {
        'hash': HexBytes('0x00'),
        'rawTransaction': HexBytes('0x00'),
        'r': 123,
        's': 123,
        'v': 27
    }
    res_mock = response_mock(HTTPStatus.OK,
                             {'data': signed_data, 'error': None})
    with mock.patch('requests.post', new=request_mock(res_mock)):
        res = wallet.sign(TX_DICT)
        assert res == AttributeDict(signed_data)


def test_sign_hash(wallet):
    sign_hash_response_data = {
        'data': {
            'messageHash': '0x0',
            'r': 123,
            's': 123,
            'v': 27,
            'signature': '0x0'
        },
        'error': None
    }
    res_mock = response_mock(HTTPStatus.OK, sign_hash_response_data)
    with mock.patch('requests.post', new=request_mock(res_mock)):
        signed_hash = wallet.sign_hash(TX_DICT)
        assert signed_hash == AttributeDict(
            {
                'messageHash': HexBytes('0x00'),
                'r': 123,
                's': 123,
                'v': 27,
                'signature': HexBytes('0x00')
            }
        )


def test_address(wallet):
    res_mock = response_mock(
        HTTPStatus.OK,
        {'data': {'address': EMPTY_ETH_ACCOUNT}, 'error': None})
    with mock.patch('requests.get', new=request_mock(res_mock)):
        assert wallet.address == EMPTY_ETH_ACCOUNT


def test_public_key(wallet):
    res_mock = response_mock(
        HTTPStatus.OK,
        {'data': {'public_key': EMPTY_ETH_ACCOUNT}, 'error': None})
    with mock.patch('requests.get', new=request_mock(res_mock)):
        assert wallet.public_key == EMPTY_ETH_ACCOUNT
