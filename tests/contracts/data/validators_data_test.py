""" SKALE validators data test """

import pytest
from tests.constants import DEFAULT_NODE_NAME, SECOND_NODE_NAME


def test_get_reward_period(skale):
    reward_period = skale.validators_data.get_reward_period()
    assert type(reward_period) is int


def test_get_delta_period(skale):
    delta_period = skale.validators_data.get_delta_period()
    assert type(delta_period) is int


@pytest.mark.skip('Temporary moved this test to manager_test.py')
def test_get_validated_array(skale):
    node_id_a = skale.nodes_data.node_name_to_index(DEFAULT_NODE_NAME)
    node_id_b = skale.nodes_data.node_name_to_index(SECOND_NODE_NAME)

    validated_array = skale.validators_data.get_validated_array(node_id_a)
    assert len(validated_array) == 1

    node_in_bytes = validated_array[0]
    validated_node_id = int.from_bytes(node_in_bytes[:14], byteorder='big')
    assert validated_node_id == node_id_b

    validated_array = skale.validators_data.get_validated_array(node_id_b)
    assert validated_array == []
