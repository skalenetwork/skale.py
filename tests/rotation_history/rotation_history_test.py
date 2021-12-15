""" SKALE node rotation test """

import json
import logging

from skale.utils.contracts_provision.main import (
    add_test4_schain_type, cleanup_nodes_schains, create_schain
)
from skale.utils.contracts_provision import DEFAULT_SCHAIN_NAME
from skale.schain_config.rotation_history import get_previous_schain_groups
from tests.rotation_history.utils import set_up_nodes, do_dkg, rotate_node

logger = logging.getLogger(__name__)


def test_get_previous_node_no_node(skale):
    assert skale.node_rotation.get_previous_node(DEFAULT_SCHAIN_NAME, 0) is None


def test_rotation_history(skale):
    cleanup_nodes_schains(skale)
    nodes, skale_instances = set_up_nodes(skale, 4)
    add_test4_schain_type(skale)
    name = create_schain(skale, random_name=True)
    # schain = skale.schains.get_by_name(name)
    # nodes_in_chain = get_nodes_for_schain(skale, name)
    group_index = skale.web3.sha3(text=name)

    do_dkg(nodes, skale_instances, group_index)

    exiting_node_index = 1
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index)

    previous_node_id = skale.node_rotation.get_previous_node(
        name,
        nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    exiting_node_index = 1
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index)

    previous_node_id = skale.node_rotation.get_previous_node(
        name,
        nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    exiting_node_index = 2
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index)

    previous_node_id = skale.node_rotation.get_previous_node(
        name,
        nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    exiting_node_index = 3
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index)

    previous_node_id = skale.node_rotation.get_previous_node(
        name,
        nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    exiting_node_index = 1
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index)

    previous_node_id = skale.node_rotation.get_previous_node(
        name,
        nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    node_groups = get_previous_schain_groups(skale, name)
    print(json.dumps(node_groups, indent=4))
    print(name)

    # assert False
