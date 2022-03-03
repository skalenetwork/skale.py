""" SKALE config test """

import mock
import pytest
from web3.auto import w3

from skale import SkaleManager
from skale.utils.web3_utils import init_web3
from skale.utils.contracts_provision import MONTH_IN_SECONDS
from skale.utils.contracts_provision.main import (
    add_test_permissions,
    add_test2_schain_type,
    cleanup_nodes,
    create_nodes,
    link_nodes_to_validator,
    setup_validator,
    _skip_evm_time,
)
from skale.utils.account_tools import generate_account
from skale.utils.contracts_provision.fake_multisig_contract import (
    deploy_fake_multisig_contract
)
from skale.wallets import Web3Wallet

from tests.constants import ENDPOINT, TEST_ABI_FILEPATH
from tests.helper import init_skale, init_skale_allocator


NUMBER_OF_NODES = 2


@pytest.fixture(scope='session')
def web3():
    """ Returns a SKALE Manager instance with provider from config """
    w3 = init_web3(ENDPOINT)
    _skip_evm_time(w3, MONTH_IN_SECONDS)
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
    ids = create_nodes(skale)
    yield ids
    cleanup_nodes(skale, ids)


@pytest.fixture
def skale_allocator(web3):
    '''Returns a SKALE Allocator instance with provider from config'''
    return init_skale_allocator(web3)


@pytest.fixture
def empty_account():
    return w3.eth.account.create()


@pytest.fixture
def failed_skale(skale):
    tmp_wait = skale.wallet.wait
    skale.wallet.sign_and_send = mock.Mock()
    skale.wallet.wait = mock.Mock(return_value={'status': 0})
    yield skale
    skale.wallet.wait = tmp_wait
