""" SKALE config test """

import pytest
from unittest import mock
from web3.auto import w3

from skale import SkaleManager

from skale.utils.account_tools import generate_account, send_eth
from skale.utils.contracts_provision.main import (
    add_test_permissions,
    add_test2_schain_type,
    cleanup_nodes,
    cleanup_schains,
    create_nodes,
    create_schain,
    link_nodes_to_validator,
    setup_validator
)
from skale.utils.contracts_provision.fake_multisig_contract import (
    deploy_fake_multisig_contract
)
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet

from tests.constants import ENDPOINT, TEST_ABI_FILEPATH
from tests.helper import init_skale, init_skale_allocator


NUMBER_OF_NODES = 2
ETH_AMOUNT_PER_NODE = 1


@pytest.fixture(scope='session')
def web3():
    """ Returns a SKALE Manager instance with provider from config """
    w3 = init_web3(ENDPOINT)
    return w3


@pytest.fixture(scope='session')
def skale(web3):
    """ Returns a SKALE Manager instance with provider from config """
    skale_obj = init_skale(web3)
    add_test_permissions(skale_obj)
    add_test2_schain_type(skale_obj)
    if skale_obj.constants_holder.get_launch_timestamp() != 0:
        skale_obj.constants_holder.set_launch_timestamp(0)
    deploy_fake_multisig_contract(skale_obj.web3, skale_obj.wallet)
    return skale_obj


@pytest.fixture(scope='session')
def validator(skale):
    return setup_validator(skale)


@pytest.fixture
def node_wallets(skale):
    wallets = []
    for i in range(NUMBER_OF_NODES):
        acc = generate_account(skale.web3)
        pk = acc['private_key']
        wallet = Web3Wallet(pk, skale.web3)
        send_eth(
            web3=skale.web3,
            wallet=skale.wallet,
            receiver_address=wallet.address,
            amount=ETH_AMOUNT_PER_NODE
        )
        wallets.append(wallet)
    return wallets


@pytest.fixture
def node_skales(skale, node_wallets):
    return [
        SkaleManager(ENDPOINT, TEST_ABI_FILEPATH, wallet)
        for wallet in node_wallets
    ]


@pytest.fixture
def nodes(skale, node_skales, validator):
    link_nodes_to_validator(skale, validator, node_skales)
    ids = create_nodes(node_skales)
    try:
        yield ids
    finally:
        cleanup_nodes(skale, ids)


@pytest.fixture
def schain(skale, nodes):
    try:
        yield create_schain(
            skale,
            schain_type=1,  # test2 should have 1 index
            random_name=True
        )
    finally:
        cleanup_schains(skale)


@pytest.fixture
def skale_allocator(web3):
    '''Returns a SKALE Allocator instance with provider from config'''
    sk_allocator = init_skale_allocator(web3)
    vesting_manager_role = sk_allocator.allocator.vesting_manager_role()
    if not skale_allocator.allocator.has_role(vesting_manager_role, sk_allocator.wallet.address):
        skale_allocator.allocator.grant_role(vesting_manager_role, sk_allocator.wallet.address)
    return sk_allocator


@pytest.fixture
def empty_account():
    return w3.eth.account.create()


@pytest.fixture
def failed_skale(skale):
    tmp_wait, tmp_sign_and_send = skale.wallet.wait, skale.wallet.sign_and_send
    skale.wallet.sign_and_send = mock.Mock(return_value='0x000000000')
    skale.wallet.wait = mock.Mock(return_value={'status': 0})
    try:
        yield skale
    finally:
        skale.wallet.sign_and_send = tmp_sign_and_send
        skale.wallet.wait = tmp_wait
