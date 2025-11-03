"""SKALE main test"""

from functools import cached_property

import pytest
from skale_contracts.projects.skale_manager import SkaleManagerContract
from web3 import HTTPProvider, LegacyWebSocketProvider, Web3

from skale import SkaleManager
from skale.contracts.manager.nodes import Nodes
from skale.contracts.skale_contract import SkaleContract
from skale.utils.helper import get_skale_manager_address
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet
from tests.constants import ENDPOINT, ETH_PRIVATE_KEY, TEST_ABI_FILEPATH

ALLOWED_SKIP_TIME_GAP = 10
MANAGER_CONTRACTS_NUMBER = 21


def test_lib_init():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    skale = SkaleManager(
        ENDPOINT, get_skale_manager_address(TEST_ABI_FILEPATH), wallet, provider_timeout=20
    )

    cached_properties = [
        attr for attr in dir(skale) if isinstance(getattr(type(skale), attr, None), cached_property)
    ]

    assert len(cached_properties) == MANAGER_CONTRACTS_NUMBER

    for prop in cached_properties:
        value = getattr(skale, prop)
        assert value is not None, f'Cached property {prop} returned None'
        assert issubclass(type(value), SkaleContract), (
            f'Cached property {prop} is not a subclass of SkaleContract'
        )

    isinstance(skale.web3.provider, HTTPProvider)

    ws_endpoint = 'ws://localhost:8545'

    skale = SkaleManager(ws_endpoint, get_skale_manager_address(TEST_ABI_FILEPATH), wallet)
    assert skale.web3.provider.websocket_timeout == 30
    assert skale.web3.provider.conn.websocket_kwargs == {'max_size': 5 * 1024 * 1024}
    assert isinstance(skale.web3.provider, LegacyWebSocketProvider)

    file_endpoint = 'file://local_file:1001'
    with pytest.raises(Exception):
        SkaleManager(file_endpoint, get_skale_manager_address(TEST_ABI_FILEPATH), wallet)


def test_contract_cache():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    skale = SkaleManager(
        ENDPOINT, get_skale_manager_address(TEST_ABI_FILEPATH), wallet, provider_timeout=20
    )
    first_access = skale.nodes
    second_access = skale.nodes
    assert first_access is second_access


def test_get_contract_address(skale):
    lib_nodes_address = skale.instance.get_contract_address(SkaleManagerContract.NODES)
    lib_nodes_address = Web3.to_checksum_address(lib_nodes_address)
    nodes_address = skale.nodes.address

    assert lib_nodes_address == nodes_address


def test_get_attr(skale):
    with pytest.raises(AttributeError):
        skale.t123_random_attr
    skale_py_nodes_contract = skale.nodes
    assert issubclass(type(skale_py_nodes_contract), SkaleContract)
    assert isinstance(skale_py_nodes_contract, Nodes)


def test_legacy_abi_generation(skale):
    abi_dict = skale._generate_legacy_abi()
    assert 'nodes_abi' in abi_dict
    assert 'nodes_address' in abi_dict
    assert isinstance(abi_dict['nodes_abi'], list)
    assert Web3.is_checksum_address(abi_dict['nodes_address'])
