""" SKALE data prep for testing """

import click

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.utils.helper import init_default_logger
from skale.utils.web3_utils import wait_receipt, check_receipt
from tests.constants import (
    DEFAULT_SCHAIN_NAME, DEFAULT_NODE_NAME,
    ENDPOINT, SECOND_NODE_NAME, TEST_ABI_FILEPATH,
    ETH_PRIVATE_KEY
)
from tests.utils import generate_random_node_data, generate_random_schain_data


def cleanup_nodes_schains(skale):
    print('Cleanup nodes and schains')
    for schain_id in skale.schains_data.get_all_schains_ids():
        schain_data = skale.schains_data.get(schain_id)
        schain_name = schain_data.get('name', None)
        if schain_name is not None:
            res = skale.manager.delete_schain(schain_name)
            receipt = wait_receipt(skale.web3, res['tx'])
            check_receipt(receipt)
    for node_id in skale.nodes_data.get_active_node_ids():
        res = skale.manager.deregister(node_id)
        receipt = wait_receipt(skale.web3, res['tx'])
        check_receipt(receipt)


def create_nodes(skale):
    # create couple of nodes
    print('Creating two nodes')
    node_names = [DEFAULT_NODE_NAME, SECOND_NODE_NAME]
    for name in node_names:
        ip, public_ip, port, _ = generate_random_node_data()
        res = skale.manager.create_node(ip, port, name, public_ip)
        receipt = wait_receipt(skale.web3, res['tx'])
        check_receipt(receipt)


def create_schain(skale):
    print('Creating schain')
    # create 1 s-chain
    type_of_nodes, lifetime_seconds, _ = generate_random_schain_data()
    price_in_wei = skale.schains.get_schain_price(type_of_nodes,
                                                  lifetime_seconds)

    res = skale.manager.create_schain(
        lifetime_seconds,
        type_of_nodes,
        price_in_wei,
        DEFAULT_SCHAIN_NAME,
    )
    receipt = wait_receipt(skale.web3, res['tx'])
    check_receipt(receipt)


@click.command()
@click.option('--cleanup-only', is_flag=True)
def prepare_data(cleanup_only):
    init_default_logger()
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    skale = Skale(ENDPOINT, TEST_ABI_FILEPATH, wallet)
    cleanup_nodes_schains(skale)
    if not cleanup_only:
        try:
            create_nodes(skale)
            create_schain(skale)
        except Exception as err:
            cleanup_nodes_schains(skale)
            raise err


if __name__ == "__main__":
    prepare_data()
