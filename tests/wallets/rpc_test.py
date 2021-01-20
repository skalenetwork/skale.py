""" SKALE RPCWallet test """


from http import HTTPStatus

import pytest
import mock

from hexbytes import HexBytes
from skale.wallets import RPCWallet
from skale.utils.exceptions import RPCWalletError

from tests.constants import (
    ENDPOINT, EMPTY_HEX_STR, ETH_PRIVATE_KEY,
    NOT_EXISTING_RPC_WALLET_URL, TEST_SGX_ENDPOINT, TEST_RPC_WALLET_URL
)
from tests.helper import response_mock, request_mock
from tests.wallets.utils import SgxClient
from skale.utils.web3_utils import (
    init_web3,
    private_key_to_address, private_key_to_public,
    to_checksum_address
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


def test_rpc_sign_hash(wallet):
    unsigned_hash = '0x31323331'
    signed_message = wallet.sign_hash(unsigned_hash)
    assert signed_message.signature == HexBytes('0x6161616161613131313131')


def test_rpc_address(wallet):
    address = to_checksum_address(
        private_key_to_address(ETH_PRIVATE_KEY)
    )
    assert wallet.address == address


def test_rpc_public_key(wallet):
    pk = private_key_to_public(ETH_PRIVATE_KEY)
    assert wallet.public_key == pk
