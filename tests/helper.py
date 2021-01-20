""" SKALE test utilities """

from dataclasses import dataclass

from mock import Mock, MagicMock

from skale import Skale, SkaleManager, SkaleAllocator
from skale.utils.account_tools import generate_account_with_balance
from skale.utils.contracts_provision.utils import (
    generate_domain,
    generate_random_ip,
    generate_random_name,
    generate_random_port,
)
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet
from tests.constants import (ENDPOINT, TEST_ABI_FILEPATH,
                             TEST_ALLOCATOR_ABI_FILEPATH,
                             ETH_PRIVATE_KEY)


@dataclass
class Node:
    skale: Skale
    name: str
    node_id: int


def response_mock(status_code=0, json_data=None, cookies=None,
                  headers=None, raw=None):
    result = MagicMock()
    result.status_code = status_code
    result.json = MagicMock(return_value=json_data)
    result.cookies = cookies
    result.headers = headers
    result.raw = raw
    return result


def request_mock(response_mock):
    return Mock(return_value=response_mock)


def init_skale(endpoint: str = ENDPOINT,
               eth_private_key: str = ETH_PRIVATE_KEY,
               test_abi_filepath: str = TEST_ABI_FILEPATH) -> SkaleManager:
    web3 = init_web3(endpoint)
    wallet = Web3Wallet(eth_private_key, web3)
    return SkaleManager(endpoint, test_abi_filepath, wallet)


def init_skale_allocator(
    endpoint: str = ENDPOINT,
    eth_private_key: str = ETH_PRIVATE_KEY,
    test_allocator_abi_filepath: str = TEST_ALLOCATOR_ABI_FILEPATH
) -> SkaleAllocator:
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    return SkaleAllocator(ENDPOINT, TEST_ALLOCATOR_ABI_FILEPATH, wallet)


def create_validator_nodes(skale, nodes_amount) -> Node:
    """ Creates nodes_amount nodes that linked to validator """
    """ with account specified by skale """
    web3 = init_web3(ENDPOINT)
    eth_amount = web3.toWei(2, 'ether')
    nodes_skales = [
        init_skale(
            ENDPOINT,
            generate_account_with_balance(
                skale.web3,
                skale.wallet,
                eth_amount
            )['private_key'],
            TEST_ABI_FILEPATH
        )
        for i in range(nodes_amount)
    ]
    validator_id = skale.validator_service.get_validator_id_by_node_address(
        skale.wallet.address
    )
    for node_skale in nodes_skales:
        skale.validator_service.link_node_address(
            node_skale.wallet.address,
            node_skale.validator_service.get_link_node_signature(validator_id)
        )

    nodes = []
    for i, node_skale in enumerate(nodes_skales):
        ip = public_ip = generate_random_ip()
        port = generate_random_port()
        name = f'{generate_random_name()}-{i}'
        domain = generate_domain()
        node_skale.manager.create_node(
            ip=ip,
            port=port,
            name=name,
            domain_name=domain,
            public_ip=public_ip,
            wait_for=True
        )
        node_id = node_skale.nodes.node_name_to_index(name)
        nodes.append(Node(node_skale, name, node_id))
    return nodes
