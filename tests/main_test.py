""" SKALE main test """

import mock
import pytest
from web3 import HTTPProvider, WebsocketProvider

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.base_contract import BaseContract
from skale.manager.contracts.nodes import Nodes
from skale.manager.contracts_info import CONTRACTS_INFO, DEBUG_CONTRACTS_INFO
from tests.constants import TEST_CONTRACT_NAME, ENDPOINT, TEST_ABI_FILEPATH, ETH_PRIVATE_KEY
from skale.utils.contracts_provision.main import _skip_evm_time


def test_lib_init():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    skale = Skale(ENDPOINT, TEST_ABI_FILEPATH, wallet, provider_timeout=20)

    lib_contracts = skale._Skale__contracts
    assert len(lib_contracts) == len(CONTRACTS_INFO) + len(DEBUG_CONTRACTS_INFO)

    for lib_contract in lib_contracts.values():
        assert issubclass(type(lib_contract), BaseContract)
        assert lib_contract.address is not None
        assert int(lib_contract.address, 16) != 0
        assert web3.eth.getCode(lib_contract.address)
        assert skale.web3.provider._request_kwargs == {'timeout': 20}

    isinstance(skale.web3.provider, HTTPProvider)

    ws_endpoint = 'ws://localhost:8080'
    with mock.patch.object(Skale, '_Skale__init_contracts'):
        skale = Skale(ws_endpoint, TEST_ABI_FILEPATH, wallet)
        assert skale.web3.provider.websocket_timeout == 30
        assert skale.web3.provider.conn.websocket_kwargs == {
            'max_size': 5 * 1024 * 1024
        }
        assert isinstance(skale.web3.provider, WebsocketProvider)

    file_endpoint = 'file://local_file:1001'
    with pytest.raises(Exception):
        Skale(file_endpoint, TEST_ABI_FILEPATH, wallet)


def test_get_contract_address(skale):
    lib_nodes_address = skale.get_contract_address(TEST_CONTRACT_NAME)
    nodes_address = skale.nodes.address

    assert lib_nodes_address == nodes_address


def test_get_attr(skale):
    random_attr = skale.t123_random_attr
    assert random_attr is None
    skale_py_nodes_contract = skale.nodes
    assert issubclass(type(skale_py_nodes_contract), BaseContract)
    assert isinstance(skale_py_nodes_contract, Nodes)


def test_skip_evm_time(skale):
    seconds = 10
    old_time = _skip_evm_time(skale.web3, 0)
    new_time = _skip_evm_time(skale.web3, seconds)
    assert new_time == old_time + seconds
