""" SKALE data prep for testing """

import click

from skale import SkaleManager
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.utils.helper import init_default_logger
from skale.utils.contracts_provision import MONTH_IN_SECONDS
from skale.utils.contracts_provision.main import (
    cleanup_nodes_schains, setup_validator,
    create_nodes, create_schain, _skip_evm_time
)
from tests.constants import ENDPOINT, TEST_ABI_FILEPATH, ETH_PRIVATE_KEY


def clean_and_restart(skale):
    cleanup_nodes_schains(skale)
    try:
        setup_validator(skale)
        create_nodes(skale)
        create_schain(skale)
    except Exception as err:
        cleanup_nodes_schains(skale)
        raise err


@click.command()
@click.option('--cleanup-only', is_flag=True)
def prepare_data(cleanup_only):
    init_default_logger()
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    skale = SkaleManager(ENDPOINT, TEST_ABI_FILEPATH, wallet)
    cleanup_nodes_schains(skale)
    if not cleanup_only:
        try:
            setup_validator(skale)
            # signature = skale.validator_service.get_link_node_signature(
            #     validator_id=D_VALIDATOR_ID
            # )
            # skale.validator_service.link_node_address(
            #     node_address=skale.wallet.address,
            #     signature=signature,
            #     wait_for=True
            # )
            # skale.time_helpers_with_debug.skip_time(MONTH_IN_SECONDS, wait_for=True)
            _skip_evm_time(skale.web3, MONTH_IN_SECONDS)
            skale.constants_holder.set_launch_timestamp(0, wait_for=True)
            create_nodes(skale)
            create_schain(skale)
            active_node_ids = skale.nodes.get_active_node_ids()
            print(active_node_ids)
        except Exception as err:
            cleanup_nodes_schains(skale)
            raise err


if __name__ == "__main__":
    prepare_data()
