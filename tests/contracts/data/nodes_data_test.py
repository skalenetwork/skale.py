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
""" SKALE node data test """

import skale.utils.helper as Helper
from skale.contracts.data.nodes_data import FIELDS
from tests.constants import DEFAULT_NODE_ID, NOT_EXIST_NODE_ID, TEST_NAME, TEST_NAME_HASH, \
    UNUSED_NAME, UNUSED_IP


def test_get_raw(skale):
    node_arr = skale.nodes_data._NodesData__get_raw(DEFAULT_NODE_ID)
    assert len(FIELDS) == len(node_arr)


def test_get_raw_not_exist(skale):
    node_arr = skale.nodes_data._NodesData__get_raw(NOT_EXIST_NODE_ID)
    assert node_arr is None


def test_get(skale):
    node = skale.nodes_data.get(DEFAULT_NODE_ID)

    assert list(node.keys()) == FIELDS
    assert [k for k, v in node.items() if v is None] == []


def test_get_by_name(skale):
    node = skale.nodes_data.get(DEFAULT_NODE_ID)
    node_name = node['name']
    node_by_name = skale.nodes_data.get_by_name(node_name)

    assert list(node_by_name.keys()) == FIELDS
    assert node == node_by_name


def test_get_active_node_ids(skale):
    active_node_ids = skale.nodes_data.get_active_node_ids()

    assert isinstance(active_node_ids, list)

    node = skale.nodes_data.get(active_node_ids[-1])
    assert list(node.keys()) == FIELDS


def test_get_active_node_ips(skale):
    active_node_ips = skale.nodes_data.get_active_node_ips()

    assert isinstance(active_node_ips, list)

    test_ip = Helper.ip_from_bytes(active_node_ips[0])
    assert Helper.is_valid_ipv4_address(test_ip)


def test_get_active_node_ids_by_address(skale, wallet):
    active_node_ids = skale.nodes_data.get_active_node_ids_by_address(wallet['address'])
    assert isinstance(active_node_ids, list)

    node = skale.nodes_data.get(active_node_ids[-1])
    assert list(node.keys()) == FIELDS


def test_name_to_id(skale):
    node_name_hash = skale.nodes_data.name_to_id(TEST_NAME)
    assert node_name_hash == TEST_NAME_HASH


def test_is_node_name_available(skale):
    node = skale.nodes_data.get(DEFAULT_NODE_ID)

    is_used_node_name_available = skale.nodes_data.is_node_name_available(node['name'])
    is_unused_node_name_available = skale.nodes_data.is_node_name_available(UNUSED_NAME)

    assert is_used_node_name_available is False
    assert is_unused_node_name_available is True


def test_is_node_ip_available(skale):
    node = skale.nodes_data.get(DEFAULT_NODE_ID)
    node_ip = Helper.ip_from_bytes(node['ip'])

    is_used_node_ip_available = skale.nodes_data.is_node_ip_available(node_ip)
    is_unused_node_ip_available = skale.nodes_data.is_node_name_available(UNUSED_IP)

    assert is_used_node_ip_available is False
    assert is_unused_node_ip_available is True

def test_node_name_to_index(skale):
    node_idx = skale.nodes_data.node_name_to_index(TEST_NAME)
    assert DEFAULT_NODE_ID == node_idx