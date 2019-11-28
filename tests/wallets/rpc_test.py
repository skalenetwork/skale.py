""" SKALE RPCWallet test """


from http import HTTPStatus
import pytest
import mock
import requests
from skale.wallets.rpc_wallet import RPCWallet
from skale.utils.exceptions import RPCWalletError

from tests.constants import (EMPTY_ETH_ACCOUNT, NOT_EXISTING_RPC_WALLET_URL, EMPTY_HEX_STR,
                             TEST_RPC_WALLET_URL)
from tests.utils import response_mock, request_mock


TX_DICT = {
    'to': '0x1057dc7277a319927D3eB43e05680B75a00eb5f4',
    'value': 9,
    'gas': 200000,
    'gasPrice': 1,
    'nonce': 7,
    'chainId': None,
    'data': '0x0'
}


def test_rpc_not_available():
    wallet = RPCWallet(NOT_EXISTING_RPC_WALLET_URL)
    with pytest.raises(requests.exceptions.ConnectionError):
        wallet.address


def test_sign_and_send():
    wallet = RPCWallet(TEST_RPC_WALLET_URL)
    res_mock = response_mock(HTTPStatus.OK,
                             {'data': {'transaction_hash': EMPTY_HEX_STR}, 'error': None})
    with mock.patch('requests.post', new=request_mock(res_mock)):
        tx_hash = wallet.sign_and_send(TX_DICT)
        assert tx_hash == EMPTY_HEX_STR


def test_sign_and_send_fail():
    wallet = RPCWallet(TEST_RPC_WALLET_URL)
    res_mock = response_mock(HTTPStatus.BAD_REQUEST, {'data': None, 'error': 'Insufficient funds'})
    with mock.patch('requests.post', new=request_mock(res_mock)):
        with pytest.raises(RPCWalletError):
            wallet.sign_and_send(TX_DICT)


def test_sign():
    wallet = RPCWallet(TEST_RPC_WALLET_URL)
    res_mock = response_mock(HTTPStatus.OK,
                             {'data': {'transaction_hash': EMPTY_HEX_STR}, 'error': None})
    with mock.patch('requests.post', new=request_mock(res_mock)):
        tx_hash = wallet.sign(TX_DICT)
        assert tx_hash == EMPTY_HEX_STR


def test_address():
    wallet = RPCWallet(TEST_RPC_WALLET_URL)
    res_mock = response_mock(HTTPStatus.OK,
                             {'data': {'address': EMPTY_ETH_ACCOUNT}, 'error': None})
    with mock.patch('requests.get', new=request_mock(res_mock)):
        assert wallet.address == EMPTY_ETH_ACCOUNT


def test_public_key():
    wallet = RPCWallet(TEST_RPC_WALLET_URL)
    res_mock = response_mock(HTTPStatus.OK,
                             {'data': {'public_key': EMPTY_ETH_ACCOUNT}, 'error': None})
    with mock.patch('requests.get', new=request_mock(res_mock)):
        assert wallet.public_key == EMPTY_ETH_ACCOUNT
