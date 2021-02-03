""" SKALE config test """

import os

import pytest
from web3.auto import w3

from tests.constants import ENDPOINT
from tests.helper import (
    create_validator_nodes, init_skale, init_skale_allocator
)
from skale.utils.web3_utils import init_web3

TEST_ABI_FILEPATH = os.getenv('TEST_ABI_FILEPATH')


@pytest.fixture
def web3():
    """ Returns a SKALE Manager instance with provider from config """
    return init_web3(ENDPOINT)


@pytest.fixture
def skale(web3):
    """ Returns a SKALE Manager instance with provider from config """
    return init_skale(web3)


@pytest.fixture
def skale_allocator(web3):
    '''Returns a SKALE Allocator instance with provider from config'''
    return init_skale_allocator(web3)


@pytest.fixture
def empty_account():
    return w3.eth.account.create()


@pytest.fixture
def nodes_on_contracts(request, skale):
    """ Creates nodes. Amount specified using mark.nodes_amount(amount) """
    marker = request.node.get_closest_marker('nodes_amount')
    if marker is None:
        nodes_amount = 1
    else:
        nodes_amount = marker.args[0]

    nodes = create_validator_nodes(skale, nodes_amount)

    yield nodes

    for node in nodes:
        node.skale.manager.node_exit(node.node_id)
