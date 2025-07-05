"""SKALE node rotation test"""

import logging

import pytest

from skale.schain_config.rotation_history import get_previous_schain_groups
from skale.utils.contracts_provision import DEFAULT_SCHAIN_NAME
from skale.utils.contracts_provision.main import (
    add_test4_schain_type,
    cleanup_nodes_schains,
    create_schain,
)
from tests.rotation_history.utils import fail_dkg, remove_node, rotate_node, run_dkg, set_up_nodes

logger = logging.getLogger(__name__)


def test_get_previous_node_no_node(skale):
    assert skale.node_rotation.get_previous_node(DEFAULT_SCHAIN_NAME, 0) is None


@pytest.fixture
def four_node_schain(skale, validator):
    nodes, skale_instances = set_up_nodes(skale, 4, no_zero_id=False)
    add_test4_schain_type(skale)
    try:
        name = create_schain(
            skale,
            schain_type=2,  # test4 type
            random_name=True,
        )
        yield nodes, skale_instances, name
    finally:
        cleanup_nodes_schains(skale)


def test_rotation_history(skale, four_node_schain):
    nodes, skale_instances, name = four_node_schain
    group_index = skale.web3.keccak(text=name)

    run_dkg(nodes, skale_instances, group_index, rotation_id=0)

    group_ids_0 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = 1
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index, rotation_id=1)

    previous_node_id = skale.node_rotation.get_previous_node(
        name, nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    group_ids_1 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = 1
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index, rotation_id=2)

    previous_node_id = skale.node_rotation.get_previous_node(
        name, nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    group_ids_2 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = 2
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index, rotation_id=3)

    previous_node_id = skale.node_rotation.get_previous_node(
        name, nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    group_ids_3 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = 3
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index, rotation_id=4)

    previous_node_id = skale.node_rotation.get_previous_node(
        name, nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    group_ids_4 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = 1
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index, rotation_id=5)

    previous_node_id = skale.node_rotation.get_previous_node(
        name, nodes[exiting_node_index]['node_id']
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
    group_index = skale.web3.keccak(text=name)

    run_dkg(nodes, skale_instances, group_index, rotation_id=0)

    group_ids_0 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = 1
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index, rotation_id=1)

    group_ids_1 = skale.schains_internal.get_node_ids_for_schain(name)

    node_groups = get_previous_schain_groups(skale, name)

    assert len(node_groups) == 2
    assert set(node_groups[0]['nodes'].keys()) == set(group_ids_0)
    assert set(node_groups[1]['nodes'].keys()) == set(group_ids_1)


@pytest.mark.parametrize(
    'first_node_index_to_exit,failed_node_index,second_node_index_to_exit',
    [(1, 2, 1), (1, 2, 3), (2, 2, 2)],
)
def test_rotation_history_failed_dkg(
    skale, four_node_schain, first_node_index_to_exit, failed_node_index, second_node_index_to_exit
):
    nodes, skale_instances, name = four_node_schain
    group_index = skale.web3.keccak(text=name)
    assert not skale.dkg.is_node_broadcasted(group_index, nodes[0]['node_id'])

    run_dkg(nodes, skale_instances, group_index, rotation_id=0)
    assert skale.dkg.is_node_broadcasted(group_index, nodes[0]['node_id'])

    group_ids_0 = skale.schains_internal.get_node_ids_for_schain(name)

    rotate_node(
        skale,
        group_index,
        nodes,
        skale_instances,
        first_node_index_to_exit,
        do_dkg=False,
        rotation_id=1,
    )

    group_ids_1 = skale.schains_internal.get_node_ids_for_schain(name)

    failed_node_id = nodes[failed_node_index]['node_id']
    fail_dkg(skale, nodes, skale_instances, group_index, failed_node_index, rotation_id=1)

    group_ids_2 = skale.schains_internal.get_node_ids_for_schain(name)

    exiting_node_index = second_node_index_to_exit
    exiting_node_id = nodes[exiting_node_index]['node_id']
    rotate_node(skale, group_index, nodes, skale_instances, exiting_node_index, rotation_id=3)

    previous_node_id = skale.node_rotation.get_previous_node(
        name, nodes[exiting_node_index]['node_id']
    )
    assert previous_node_id == exiting_node_id

    group_ids_3 = skale.schains_internal.get_node_ids_for_schain(name)

    remove_node(skale, failed_node_id)

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
