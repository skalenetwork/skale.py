""" SKALE node rotation test """

import logging

import pytest

from skale.utils.contracts_provision.main import (
    add_test4_schain_type, cleanup_nodes_schains, create_schain
)
from skale.utils.contracts_provision import DEFAULT_SCHAIN_NAME
from skale.schain_config.rotation_history import get_previous_schain_groups, get_new_nodes_list
from tests.rotation_history.utils import (
    set_up_nodes,
    run_dkg,
    remove_node,
    rotate_node,
    fail_dkg
)

logger = logging.getLogger(__name__)


def test_get_previous_node_no_node(skale):
    assert skale.node_rotation.get_previous_node(DEFAULT_SCHAIN_NAME, 0) is None


@pytest.fixture
def four_node_schain(skale, validator):
    nodes, skale_instances = set_up_nodes(skale, 4)
    add_test4_schain_type(skale)
    try:
        name = create_schain(
            skale,
            schain_type=2,  # test4 type
            random_name=True
        )
        yield nodes, skale_instances, name
    finally:
        cleanup_nodes_schains(skale)


def test_rotation_history(skale, four_node_schain):
    nodes, skale_instances, name = four_node_schain
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


def test_rotation_history_no_rotations(skale, four_node_schain):
    _, _, name = four_node_schain
    node_groups = get_previous_schain_groups(skale, name)
    group_ids = skale.schains_internal.get_node_ids_for_schain(name)

    assert len(node_groups) == 1
    assert set(node_groups[0]['nodes'].keys()) == set(group_ids)


def test_rotation_history_single_rotation(skale, four_node_schain):
    nodes, skale_instances, name = four_node_schain
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


def test_rotation_history_failed_dkg(skale, four_node_schain):
    nodes, skale_instances, name = four_node_schain
    group_index = skale.web3.sha3(text=name)

    run_dkg(nodes, skale_instances, group_index)

    group_ids_0 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = 1
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index, do_dkg=False)

    group_ids_1 = skale.schains_internal.get_node_ids_for_schain(name)

    failed_node_index = 2
    fail_dkg(skale, nodes, skale_instances, group_index, failed_node_index)

    group_ids_2 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = 1
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index)

    previous_node_id = skale.node_rotation.get_previous_node(
        name,
        nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    group_ids_3 = skale.schains_internal.get_node_ids_for_schain(name)

    node_groups = get_previous_schain_groups(skale, name)

    assert len(node_groups) == 4
    assert set(node_groups[0]['nodes'].keys()) == set(group_ids_0)
    assert set(node_groups[1]['nodes'].keys()) == set(group_ids_1)
    assert set(node_groups[2]['nodes'].keys()) == set(group_ids_2)
    assert set(node_groups[3]['nodes'].keys()) == set(group_ids_3)

    assert node_groups[0]['finish_ts']
    assert node_groups[0]['bls_public_key']

    # no keys and finish_ts because it's the group that failed DKG
    assert not node_groups[1]['finish_ts']
    assert not node_groups[1]['bls_public_key']

    assert node_groups[2]['finish_ts']
    assert node_groups[2]['bls_public_key']

    # no finish_ts because it's the current group
    assert not node_groups[3]['finish_ts']
    assert node_groups[3]['bls_public_key']


def test_get_new_nodes_list(skale, four_node_schain):
    nodes, skale_instances, name = four_node_schain
    group_index = skale.web3.sha3(text=name)

    run_dkg(nodes, skale_instances, group_index)

    exiting_node_index = 1
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index, do_dkg=False)

    failed_node_index = 2
    second_failed_node_index = 3
    test_new_node_ids = fail_dkg(
        skale=skale,
        nodes=nodes,
        skale_instances=skale_instances,
        group_index=group_index,
        failed_node_index=failed_node_index,
        second_failed_node_index=second_failed_node_index
    )

    rotation = skale.node_rotation.get_rotation_obj(name)
    node_groups = get_previous_schain_groups(
        skale=skale,
        schain_name=name,
        leaving_node_id=rotation.leaving_node_id,
        include_keys=False
    )
    new_nodes = get_new_nodes_list(skale, name, node_groups)

    assert len(new_nodes) == 3
    assert all(x in new_nodes for x in test_new_node_ids)

    # Temorary fix for "The schain does not exist" problem
    # Bad nodes should be removed before chain is deleted
    remove_node(skale, nodes[exiting_node_index]['node_id'])
    remove_node(skale, nodes[failed_node_index]['node_id'])
    remove_node(skale, nodes[second_failed_node_index]['node_id'])

    exiting_node_index = 3
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index)

    rotation = skale.node_rotation.get_rotation_obj(name)
    node_groups = get_previous_schain_groups(
        skale=skale,
        schain_name=name,
        leaving_node_id=rotation.leaving_node_id,
        include_keys=False
    )
    new_nodes = get_new_nodes_list(skale, name, node_groups)

    assert len(new_nodes) == 1
