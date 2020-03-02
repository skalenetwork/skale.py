""" SKALE data prep for testing """

import click

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.utils.helper import init_default_logger
from skale.utils.contracts_provision.main import (
    cleanup_nodes_schains, setup_validator, create_nodes, create_schain
)
from tests.constants import ENDPOINT, TEST_ABI_FILEPATH, ETH_PRIVATE_KEY


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
            setup_validator(skale)
            create_nodes(skale)
            create_schain(skale)
        except Exception as err:
            cleanup_nodes_schains(skale)
            raise err


if __name__ == "__main__":
    prepare_data()
