""" SKALE config test """

import os

import pytest
from web3.auto import w3

from tests.helper import (
    create_validator_nodes, init_skale, init_skale_allocator
)


ENDPOINT = os.getenv('ENDPOINT')
TEST_ABI_FILEPATH = os.getenv('TEST_ABI_FILEPATH')


@pytest.fixture
def skale():
    '''Returns a SKALE Manager instance with provider from config'''
    return init_skale()


@pytest.fixture
def skale_allocator():
    '''Returns a SKALE Allocator instance with provider from config'''
    return init_skale_allocator()


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
