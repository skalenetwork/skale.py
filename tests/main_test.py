""" SKALE main test """

import mock
import pytest
from web3 import HTTPProvider, WebsocketProvider

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.contracts import BaseContract
from skale.contracts.functionality.nodes import Nodes
from skale.contracts_info import CONTRACTS_INFO
from skale.utils.contract_info import ContractInfo
from tests.constants import TEST_CONTRACT_NAME, ENDPOINT, TEST_ABI_FILEPATH, ETH_PRIVATE_KEY


def test_lib_init():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    skale = Skale(ENDPOINT, TEST_ABI_FILEPATH, wallet, provider_timeout=20)

    lib_contracts_info = skale._Skale__contracts_info
    for contract_info in CONTRACTS_INFO:
        assert isinstance(lib_contracts_info[contract_info.name], ContractInfo)

    lib_contracts = skale._Skale__contracts
    assert len(lib_contracts) == len(CONTRACTS_INFO)

    for lib_contract in lib_contracts.values():
        assert issubclass(type(lib_contract), BaseContract)
        assert lib_contract.address is not None
        assert int(lib_contract.address, 16) != 0
        assert web3.eth.getCode(lib_contract.address)
        assert lib_contract.abi is not None
        assert skale.web3.provider.websocket_timeout == 20
        assert skale.web3.provider.conn.websocket_kwargs == {
            'max_size': 5 * 1024 * 1024
        }

    assert skale.abi is not None

    provider = skale.web3.provider
    assert isinstance(provider, WebsocketProvider) or isinstance(provider, HTTPProvider)

    http_endpoint = 'http://localhost:8080'
    with mock.patch.object(Skale, '_Skale__init_contracts'):
        skale = Skale(http_endpoint, TEST_ABI_FILEPATH, wallet)
        provider = skale.web3.provider
        assert provider._request_kwargs == {'timeout': 30}
        assert isinstance(provider, HTTPProvider)

    file_endpoint = 'file://local_file:1001'
    with pytest.raises(Exception):
        Skale(file_endpoint, TEST_ABI_FILEPATH, wallet)


def test_get_contract_address(skale):
    lib_nodes_functionality_address = skale.get_contract_address(TEST_CONTRACT_NAME)
    nodes_functionality_address = skale.nodes.address

    assert lib_nodes_functionality_address == nodes_functionality_address


def test_get_attr(skale):
    random_attr = skale.t123_random_attr
    assert random_attr is None
    skale_py_nodes_contract = skale.nodes
    assert issubclass(type(skale_py_nodes_contract), BaseContract)
    assert isinstance(skale_py_nodes_contract, Nodes)
