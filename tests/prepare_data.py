""" SKALE data prep for testing """

import click

from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.utils.helper import init_default_logger
from skale.utils.web3_utils import check_receipt
from tests.constants import (
    DEFAULT_SCHAIN_NAME, DEFAULT_NODE_NAME, ENDPOINT, SECOND_NODE_NAME, TEST_ABI_FILEPATH,
    D_VALIDATOR_ID, ETH_PRIVATE_KEY, D_VALIDATOR_NAME, D_VALIDATOR_DESC, D_VALIDATOR_FEE,
    D_VALIDATOR_MIN_DEL, D_DELEGATION_PERIOD, D_DELEGATION_INFO
)
from tests.utils import generate_random_node_data, generate_random_schain_data


def cleanup_nodes_schains(skale):
    print('Cleanup nodes and schains')
    for schain_id in skale.schains_data.get_all_schains_ids():
        schain_data = skale.schains_data.get(schain_id)
        schain_name = schain_data.get('name', None)
        if schain_name is not None:
            tx_res = skale.manager.delete_schain(schain_name, wait_for=True)
            check_receipt(tx_res.receipt)
    for node_id in skale.nodes_data.get_active_node_ids():
        tx_res = skale.manager.deregister(node_id, wait_for=True)
        check_receipt(tx_res.receipt)


def validator_exist(skale):
    return skale.validator_service.number_of_validators() > 0


def setup_validator(skale):
    """Create and activate a validator"""
    if not validator_exist(skale):
        create_validator(skale)
        enable_validator(skale)
    delegation_id = len(skale.delegation_service.get_all_delegations_by_validator(
        skale.wallet.address))
    set_test_msr(skale)
    delegate_to_validator(skale)
    accept_pending_delegation(skale, delegation_id)
    skip_delegation_delay(skale, delegation_id)


def link_address_to_validator(skale):
    print('Linking address to validator')
    tx_res = skale.delegation_service.link_node_address(
        node_address=skale.wallet.address,
        wait_for=True
    )
    check_receipt(tx_res.receipt)


def skip_delegation_delay(skale, delegation_id):
    print(f'Activating delegation with ID {delegation_id}')
    tx_res = skale.token_state._skip_transition_delay(
        delegation_id,
        wait_for=True
    )
    check_receipt(tx_res.receipt)


def accept_pending_delegation(skale, delegation_id):
    print(f'Accepting delegation with ID: {delegation_id}')
    tx_res = skale.delegation_service.accept_pending_delegation(
        delegation_id=delegation_id,
        wait_for=True
    )
    check_receipt(tx_res.receipt)


def get_test_delegation_amount(skale):
    msr = skale.constants_holder.msr()
    return msr * 10


def set_test_msr(skale):
    skale.constants_holder._set_msr(
        new_msr=D_VALIDATOR_MIN_DEL,
        wait_for=True
    )


def delegate_to_validator(skale):
    print(f'Delegating tokens to validator ID: {D_VALIDATOR_ID}')
    tx_res = skale.delegation_service.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=get_test_delegation_amount(skale),
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True
    )
    check_receipt(tx_res.receipt)


def enable_validator(skale):
    print(f'Enabling validator ID: {D_VALIDATOR_ID}')
    tx_res = skale.validator_service._enable_validator(D_VALIDATOR_ID, wait_for=True)
    check_receipt(tx_res.receipt)


def create_validator(skale):
    print('Creating default validator')
    tx_res = skale.delegation_service.register_validator(
        name=D_VALIDATOR_NAME,
        description=D_VALIDATOR_DESC,
        fee_rate=D_VALIDATOR_FEE,
        min_delegation_amount=D_VALIDATOR_MIN_DEL,
        wait_for=True
    )
    check_receipt(tx_res.receipt)


def create_nodes(skale):
    # create couple of nodes
    print('Creating two nodes')
    node_names = [DEFAULT_NODE_NAME, SECOND_NODE_NAME]
    for name in node_names:
        ip, public_ip, port, _ = generate_random_node_data()
        tx_res = skale.manager.create_node(ip, port, name, public_ip,
                                           wait_for=True)
        check_receipt(tx_res.receipt)


def create_schain(skale):
    print('Creating schain')
    # create 1 s-chain
    type_of_nodes, lifetime_seconds, _ = generate_random_schain_data()
    price_in_wei = skale.schains.get_schain_price(type_of_nodes,
                                                  lifetime_seconds)

    tx_res = skale.manager.create_schain(
        lifetime_seconds,
        type_of_nodes,
        price_in_wei,
        DEFAULT_SCHAIN_NAME,
        wait_for=True
    )
    check_receipt(tx_res.receipt)


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
