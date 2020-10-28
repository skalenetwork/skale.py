""" SKALE RPCWallet test """


from http import HTTPStatus
import pytest
import mock

from hexbytes import HexBytes
from eth_account.datastructures import AttributeDict

from skale.wallets.rpc_wallet import RPCWallet
from skale.utils.exceptions import RPCWalletError

from tests.constants import (EMPTY_ETH_ACCOUNT, NOT_EXISTING_RPC_WALLET_URL, EMPTY_HEX_STR,
                             TEST_RPC_WALLET_URL)
from tests.helper import response_mock, request_mock


TX_DICT = {
    'to': '0x1057dc7277a319927D3eB43e05680B75a00eb5f4',
    'value': 9,
    'gas': 200000,
    'gasPrice': 1,
    'nonce': 7,
    'chainId': None,
    'data': '0x0'
}

TEST_MAX_RETRIES = 3


def test_rpc_not_available():
    wallet = RPCWallet(NOT_EXISTING_RPC_WALLET_URL)
    with pytest.raises(RPCWalletError):
        wallet.address


def test_sign_and_send():
    wallet = RPCWallet(TEST_RPC_WALLET_URL)
    res_mock = response_mock(HTTPStatus.OK,
                             {'data': {'transaction_hash': EMPTY_HEX_STR}, 'error': None})
    with mock.patch('requests.post', new=request_mock(res_mock)):
        tx_hash = wallet.sign_and_send(TX_DICT)
        assert tx_hash == EMPTY_HEX_STR


def test_sign_and_send_fails():
    wallet = RPCWallet(TEST_RPC_WALLET_URL, retry_if_failed=True)

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


def test_sign_and_send_sgx_unreachable_no_retries():
    wallet = RPCWallet(TEST_RPC_WALLET_URL)
    res_mock = response_mock(
        HTTPStatus.BAD_REQUEST,
        {'data': None, 'error': 'Sgx server is unreachable'}
    )
    with mock.patch('requests.post', new=request_mock(res_mock)):
        with pytest.raises(RPCWalletError):
            wallet.sign_and_send(TX_DICT)
            assert res_mock.call_count == 1


def test_sign_and_send_sgx_unreachable():
    wallet = RPCWallet(TEST_RPC_WALLET_URL, retry_if_failed=True)

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


def test_sign():
    signed_data = {
        'hash': HexBytes('0x00'),
        'rawTransaction': HexBytes('0x00'),
        'r': 123,
        's': 123,
        'v': 27
    }
    wallet = RPCWallet(TEST_RPC_WALLET_URL)
    res_mock = response_mock(HTTPStatus.OK,
                             {'data': signed_data, 'error': None})
    with mock.patch('requests.post', new=request_mock(res_mock)):
        res = wallet.sign(TX_DICT)
        assert res == AttributeDict(signed_data)


def test_sign_hash():
    wallet = RPCWallet(TEST_RPC_WALLET_URL)
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


def test_address():
    wallet = RPCWallet(TEST_RPC_WALLET_URL)
    res_mock = response_mock(
        HTTPStatus.OK,
        {'data': {'address': EMPTY_ETH_ACCOUNT}, 'error': None}
    )
    with mock.patch('requests.get', new=request_mock(res_mock)):
        assert wallet.address == EMPTY_ETH_ACCOUNT


def test_public_key():
    wallet = RPCWallet(TEST_RPC_WALLET_URL)
    res_mock = response_mock(
        HTTPStatus.OK,
        {'data': {'public_key': EMPTY_ETH_ACCOUNT}, 'error': None}
    )
    with mock.patch('requests.get', new=request_mock(res_mock)):
        assert wallet.public_key == EMPTY_ETH_ACCOUNT
