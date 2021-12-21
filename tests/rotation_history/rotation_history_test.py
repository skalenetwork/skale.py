""" SKALE node rotation test """

import logging

from skale.utils.contracts_provision.main import (
    add_test4_schain_type, cleanup_nodes_schains, create_schain, add_test2_schain_type
)
from skale.utils.contracts_provision import DEFAULT_SCHAIN_NAME
from skale.schain_config.rotation_history import get_previous_schain_groups
from tests.rotation_history.utils import set_up_nodes, run_dkg, rotate_node, fail_dkg

logger = logging.getLogger(__name__)


def test_get_previous_node_no_node(skale):
    assert skale.node_rotation.get_previous_node(DEFAULT_SCHAIN_NAME, 0) is None


def test_rotation_history(skale):
    cleanup_nodes_schains(skale)
    nodes, skale_instances = set_up_nodes(skale, 4)
    add_test4_schain_type(skale)
    name = create_schain(skale, random_name=True)
    group_index = skale.web3.sha3(text=name)

    run_dkg(nodes, skale_instances, group_index)

    group_ids_0 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = 1
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index)

    previous_node_id = skale.node_rotation.get_previous_node(
        name,
        nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    group_ids_1 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = 1
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index)

    previous_node_id = skale.node_rotation.get_previous_node(
        name,
        nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    group_ids_2 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = 2
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index)

    previous_node_id = skale.node_rotation.get_previous_node(
        name,
        nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    group_ids_3 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = 3
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index)

    previous_node_id = skale.node_rotation.get_previous_node(
        name,
        nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    group_ids_4 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = 1
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index)

    previous_node_id = skale.node_rotation.get_previous_node(
        name,
        nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    group_ids_5 = skale.schains_internal.get_node_ids_for_schain(name)

    node_groups = get_previous_schain_groups(skale, name)

    assert len(node_groups) == 6
    assert set(node_groups[0]['nodes'].keys()) == set(group_ids_0)
    assert set(node_groups[1]['nodes'].keys()) == set(group_ids_1)
    assert set(node_groups[2]['nodes'].keys()) == set(group_ids_2)
    assert set(node_groups[3]['nodes'].keys()) == set(group_ids_3)
    assert set(node_groups[4]['nodes'].keys()) == set(group_ids_4)
    assert set(node_groups[5]['nodes'].keys()) == set(group_ids_5)


def test_rotation_history_no_rotations(skale):
    cleanup_nodes_schains(skale)
    set_up_nodes(skale, 2)
    add_test2_schain_type(skale)
    name = create_schain(skale, random_name=True)

    node_groups = get_previous_schain_groups(skale, name)
    group_ids = skale.schains_internal.get_node_ids_for_schain(name)

    assert len(node_groups) == 1
    assert set(node_groups[0]['nodes'].keys()) == set(group_ids)


def test_rotation_history_single_rotation(skale):
    cleanup_nodes_schains(skale)
    nodes, skale_instances = set_up_nodes(skale, 4)
    add_test4_schain_type(skale)
    name = create_schain(skale, random_name=True)
    group_index = skale.web3.sha3(text=name)

    run_dkg(nodes, skale_instances, group_index)

    group_ids_0 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = 1
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index)

    group_ids_1 = skale.schains_internal.get_node_ids_for_schain(name)

    node_groups = get_previous_schain_groups(skale, name)

    assert len(node_groups) == 2
    assert set(node_groups[0]['nodes'].keys()) == set(group_ids_0)
    assert set(node_groups[1]['nodes'].keys()) == set(group_ids_1)


def test_rotation_history_failed_dkg(skale):
    cleanup_nodes_schains(skale)
    nodes, skale_instances = set_up_nodes(skale, 4)
    add_test4_schain_type(skale)
    name = create_schain(skale, random_name=True)
    group_index = skale.web3.sha3(text=name)

    run_dkg(nodes, skale_instances, group_index)

    group_ids_0 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = 1
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index, do_dkg=False)

    group_ids_1 = skale.schains_internal.get_node_ids_for_schain(name)

    failed_node_index = 2
    fail_dkg(skale, nodes, skale_instances, group_index, failed_node_index)

    # group_ids_2 = skale.schains_internal.get_node_ids_for_schain(name)

    node_groups = get_previous_schain_groups(skale, name)

    print(node_groups)

    # assert False

    assert len(node_groups) == 3
    assert set(node_groups[0]['nodes'].keys()) == set(group_ids_0)
    assert set(node_groups[1]['nodes'].keys()) == set(group_ids_1)
    assert set(node_groups[2]['nodes'].keys()) == set(group_ids_1)
