"""SKALE config test"""

from unittest import mock

import pytest
from web3.auto import w3

from skale import SkaleManager
from skale.utils.account_tools import generate_account, send_eth
from skale.utils.contracts_provision.fake_multisig_contract import deploy_fake_multisig_contract
from skale.utils.contracts_provision.main import (
    add_test2_schain_type,
    add_test_permissions,
    cleanup_nodes,
    cleanup_schains,
    create_nodes,
    create_schain,
    link_nodes_to_validator,
    set_automining,
    set_default_mining_interval,
    set_mining_interval,
    setup_validator,
)
from skale.utils.contracts_provision.utils import generate_random_node_data
from skale.utils.helper import get_skale_manager_address
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet
from tests.constants import ENDPOINT, TEST_ABI_FILEPATH
from tests.helper import init_fair, init_skale, init_skale_allocator

ETH_AMOUNT_PER_NODE = 1


@pytest.fixture(scope='session')
def web3():
    """Returns a SKALE Manager instance with provider from config"""
    w3 = init_web3(ENDPOINT)
    return w3


@pytest.fixture(scope='session')
def skale(web3, request):
    """Returns a cached SKALE Manager instance with provider from config"""
    if not hasattr(request.config, '_cached_skale'):
        skale_obj = init_skale(web3)
        add_test_permissions(skale_obj)
        add_test2_schain_type(skale_obj)
        if skale_obj.constants_holder.get_launch_timestamp() != 0:
            skale_obj.constants_holder.set_launch_timestamp(0)
        deploy_fake_multisig_contract(skale_obj.web3, skale_obj.wallet)
        request.config._cached_skale = skale_obj
    return request.config._cached_skale


@pytest.fixture(scope='session')
def fair(web3):
    return init_fair(web3)


@pytest.fixture(scope='session')
def validator(skale):
    return setup_validator(skale)


@pytest.fixture(scope='session')
def number_of_nodes():
    return 2


@pytest.fixture
def node_wallets(skale, number_of_nodes):
    wallets = []
    for i in range(number_of_nodes):
        acc = generate_account(skale.web3)
        pk = acc['private_key']
        wallet = Web3Wallet(pk, skale.web3)
        send_eth(
            web3=skale.web3,
            wallet=skale.wallet,
            receiver_address=wallet.address,
            amount=ETH_AMOUNT_PER_NODE,
        )
        wallets.append(wallet)
    return wallets


@pytest.fixture
def node_skales(skale, node_wallets):
    return [
        SkaleManager(ENDPOINT, get_skale_manager_address(TEST_ABI_FILEPATH), wallet)
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
def fair_active_nodes(fair, node_wallets):
    main_wallet = fair.wallet

    for wallet in node_wallets:
        fair.wallet = wallet
        ip, _, port, _ = generate_random_node_data()
        self_stake_requirement = fair.staking.self_stake_requirement()
        fair.nodes.register_active(ip=ip, port=port, value=self_stake_requirement)

    fair.wallet = main_wallet
    try:
        yield node_wallets
    finally:
        """TODO: Remove the node from the fair instance."""


@pytest.fixture
def fair_passive_nodes(fair, node_wallets):
    main_wallet = fair.wallet

    for wallet in node_wallets:
        fair.wallet = wallet
        ip, _, port, _ = generate_random_node_data()
        fair.nodes.register_passive(ip=ip, port=port)

    fair.wallet = main_wallet
    try:
        yield node_wallets
    finally:
        """TODO: Remove the node from the fair instance."""


@pytest.fixture
def schain(skale, nodes):
    try:
        yield create_schain(
            skale,
            schain_type=1,  # test2 should have 1 index
            random_name=True,
        )
    finally:
        cleanup_schains(skale)


@pytest.fixture
def skale_allocator(web3):
    """Returns a SKALE Allocator instance with provider from config"""
    return init_skale_allocator(web3)


@pytest.fixture
def empty_account():
    return w3.eth.account.create()


@pytest.fixture
def failed_skale(skale):
    tmp_wait, tmp_sign_and_send = skale.wallet.wait, skale.wallet.sign_and_send
    skale.wallet.sign_and_send = mock.Mock(return_value='0x000000000')
    skale.wallet.wait = mock.Mock(return_value={'status': 0, 'error': 'Test error'})
    try:
        yield skale
    finally:
        skale.wallet.sign_and_send = tmp_sign_and_send
        skale.wallet.wait = tmp_wait


@pytest.fixture
def block_in_seconds(skale):
    # Mine block every three seconds without automine
    # Makes web3.py throw exception in a same way as for geth
    try:
        set_automining(skale.web3, False)
        set_mining_interval(skale.web3, 3)
        yield
    finally:
        set_automining(skale.web3, True)
        set_default_mining_interval(skale.web3)
