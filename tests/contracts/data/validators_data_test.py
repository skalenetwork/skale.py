#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
