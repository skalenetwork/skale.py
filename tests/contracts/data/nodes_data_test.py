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
from tests.constants import DEFAULT_NODE_HASH, DEFAULT_NODE_NAME


def test_get_raw_not_exist(skale_wallet_with_nodes_schain):
    skale, _ = skale_wallet_with_nodes_schain
    not_exist_node_id = 123123
    node_arr = skale.nodes_data._NodesData__get_raw(not_exist_node_id)
    assert node_arr is None


def test_get(skale_wallet_with_nodes_schain):
    skale, _ = skale_wallet_with_nodes_schain
    node = skale.nodes_data.get_by_name(DEFAULT_NODE_NAME)
    node_id = skale.nodes_data.node_name_to_index(DEFAULT_NODE_NAME)
    node_by_id = skale.nodes_data.get(node_id)
    assert list(node.keys()) == FIELDS
    assert [k for k, v in node.items() if v is None] == []

    assert list(node_by_id.keys()) == FIELDS
    assert node == node_by_id


def test_get_by_name(skale_wallet_with_nodes_schain):
    skale, _ = skale_wallet_with_nodes_schain
    node = skale.nodes_data.get_by_name(DEFAULT_NODE_NAME)

    assert list(node.keys()) == FIELDS
    assert node['name'] == DEFAULT_NODE_NAME


def test_get_active_node_ids(skale_wallet_with_nodes_schain):
    skale, _ = skale_wallet_with_nodes_schain
    active_node_ids = skale.nodes_data.get_active_node_ids()

    assert isinstance(active_node_ids, list)

    node = skale.nodes_data.get(active_node_ids[-1])
    assert list(node.keys()) == FIELDS


def test_get_active_node_ips(skale_wallet_with_nodes_schain):
    skale, wallet = skale_wallet_with_nodes_schain
    active_node_ips = skale.nodes_data.get_active_node_ips()

    assert isinstance(active_node_ips, list)

    test_ip = Helper.ip_from_bytes(active_node_ips[0])
    assert Helper.is_valid_ipv4_address(test_ip)


def test_get_active_node_ids_by_address(skale_wallet_with_nodes_schain):
    skale, wallet = skale_wallet_with_nodes_schain
    active_node_ids = skale.nodes_data.get_active_node_ids_by_address(
        wallet['address']
    )
    assert isinstance(active_node_ids, list)

    node = skale.nodes_data.get(active_node_ids[-1])
    assert list(node.keys()) == FIELDS


def test_name_to_id(skale_wallet_with_nodes_schain):
    skale, _ = skale_wallet_with_nodes_schain
    node_name_hash = skale.nodes_data.name_to_id(DEFAULT_NODE_NAME)
    expected = DEFAULT_NODE_HASH
    assert node_name_hash == expected


def test_is_node_name_available(skale_wallet_with_nodes_schain):
    skale, _ = skale_wallet_with_nodes_schain
    node = skale.nodes_data.get_by_name(DEFAULT_NODE_NAME)
    unused_name = 'unused_name'
    assert skale.nodes_data.is_node_name_available(node['name']) is False
    assert skale.nodes_data.is_node_name_available(unused_name) is True


def test_is_node_ip_available(skale_wallet_with_nodes_schain):
    skale, _ = skale_wallet_with_nodes_schain
    node = skale.nodes_data.get_by_name(DEFAULT_NODE_NAME)
    node_ip = Helper.ip_from_bytes(node['ip'])

    unused_ip = '123.123.231.123'
    assert skale.nodes_data.is_node_ip_available(node_ip) is False
    assert skale.nodes_data.is_node_name_available(unused_ip) is True


def test_node_name_to_index(skale_wallet_with_nodes_schain):
    skale, _ = skale_wallet_with_nodes_schain
    node_id = skale.nodes_data.node_name_to_index(DEFAULT_NODE_NAME)
    node_by_id_data = skale.nodes_data.get(node_id)
    node_by_name_data = skale.nodes_data.get_by_name(DEFAULT_NODE_NAME)
    assert node_by_id_data == node_by_name_data
