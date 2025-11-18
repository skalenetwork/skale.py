"""SKALE node rotation test"""

from unittest import mock

import pytest

from skale.contracts.manager.node_rotation import Rotation
from skale.utils.contracts_provision.main import (
    add_test4_schain_type,
    cleanup_nodes_schains,
    create_schain,
)
from tests.constants import DEFAULT_SCHAIN_HASH, DEFAULT_SCHAIN_INDEX, DEFAULT_SCHAIN_NAME
from tests.rotation_history.utils import TEST_ROTATION_DELAY, _skip_evm_time, run_dkg, set_up_nodes


def test_get_rotation(skale):
    assert skale.node_rotation.get_rotation(DEFAULT_SCHAIN_NAME) == Rotation(
        leaving_node_id=0, new_node_id=0, freeze_until=0, rotation_counter=0
    )


def test_get_leaving_history(skale):
    empty = skale.node_rotation.get_leaving_history(DEFAULT_SCHAIN_INDEX)
    assert empty == []
    with mock.patch.object(
        skale.node_rotation.contract.functions.getLeavingHistory, 'call'
    ) as call_mock:
        call_mock.return_value = [(DEFAULT_SCHAIN_HASH, 1000), (DEFAULT_SCHAIN_HASH, 2000)]
        history = skale.node_rotation.get_leaving_history(DEFAULT_SCHAIN_INDEX)
        assert isinstance(history, list)
        assert history == [
            {'schain_id': DEFAULT_SCHAIN_HASH, 'finished_rotation': 1000},
            {'schain_id': DEFAULT_SCHAIN_HASH, 'finished_rotation': 2000},
        ]


def test_is_rotation_in_progress(skale):
    assert skale.node_rotation.is_rotation_in_progress(DEFAULT_SCHAIN_NAME) is False


def test_wait_for_new_node(skale):
    assert skale.node_rotation.wait_for_new_node(DEFAULT_SCHAIN_NAME) is False


@pytest.fixture
def four_node_schain(skale, validator):
    nodes, skale_instances = set_up_nodes(skale, 4, no_zero_id=False)
    add_test4_schain_type(skale)
    try:
        name = create_schain(
            skale,
            schain_type=2,  # test4 should have 2 index
            random_name=True,
        )
        yield nodes, skale_instances, name
    finally:
        cleanup_nodes_schains(skale)


def test_is_rotation_active(skale, four_node_schain):
    nodes, skale_instances, name = four_node_schain
    group_index = skale.web3.keccak(text=name)

    run_dkg(nodes, skale_instances, group_index)

    exiting_node_index = 3
    new_nodes, new_skale_instances = set_up_nodes(skale, 1, no_zero_id=False)

    assert not skale.node_rotation.is_new_node_found(name)
    assert not skale.node_rotation.is_rotation_in_progress(name)
    assert not skale.node_rotation.is_rotation_active(name)

    skale.nodes.init_exit(nodes[exiting_node_index]['node_id'])

    assert not skale.node_rotation.is_new_node_found(name)
    assert skale.node_rotation.is_rotation_in_progress(name)
    assert not skale.node_rotation.is_rotation_active(name)

    skale_instances[exiting_node_index].manager.node_exit(nodes[exiting_node_index]['node_id'])

    assert skale.node_rotation.is_new_node_found(name)
    assert skale.node_rotation.is_rotation_in_progress(name)
    assert skale.node_rotation.is_rotation_active(name)

    nodes[exiting_node_index] = new_nodes[0]
    skale_instances[exiting_node_index] = new_skale_instances[0]

    run_dkg(nodes, skale_instances, group_index, skip_time=False, rotation_id=1)

    assert skale.node_rotation.is_new_node_found(name)
    assert skale.node_rotation.is_rotation_in_progress(name)
    assert skale.node_rotation.is_rotation_active(name)

    _skip_evm_time(skale.web3, TEST_ROTATION_DELAY)

    assert skale.node_rotation.is_new_node_found(name)
    assert not skale.node_rotation.is_rotation_in_progress(name)
    assert not skale.node_rotation.is_rotation_active(name)
