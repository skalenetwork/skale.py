""" SKALE node test """

import socket

import pytest
from eth_keys import keys
from web3 import Web3

import skale.utils.helper as Helper
from skale.contracts.manager.nodes import FIELDS
from skale.utils.exceptions import InvalidNodeIdError
from tests.constants import DEFAULT_NODE_HASH, DEFAULT_NODE_NAME, NOT_EXISTING_ID


def test_get_raw_not_exist(skale):
    node_arr = skale.nodes._Nodes__get_raw(NOT_EXISTING_ID)
    assert node_arr is None


def public_key_from_private(key):
    pr_bytes = Web3.toBytes(hexstr=key)
    return keys.PrivateKey(pr_bytes)


def test_get(skale):
    node = skale.nodes.get_by_name(DEFAULT_NODE_NAME)
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    node_by_id = skale.nodes.get(node_id)
    assert list(node.keys()) == FIELDS
    assert [k for k, v in node.items() if v is None] == []
    assert node_by_id['name'] == DEFAULT_NODE_NAME
    socket.inet_ntoa(node_by_id['ip'])
    socket.inet_ntoa(node_by_id['publicIP'])

    assert node_by_id['publicKey'] == skale.wallet.public_key

    assert node_by_id['publicKey'] != b''
    assert node_by_id['start_block'] > 0
    assert node_by_id['last_reward_date'] > 0
    assert node_by_id['finish_time'] == 0
    assert node_by_id['status'] == 0
    assert node_by_id['validator_id'] == 1

    assert list(node_by_id.keys()) == FIELDS
    assert node == node_by_id

    with pytest.raises(InvalidNodeIdError):
        skale.nodes.get(NOT_EXISTING_ID)


def test_get_by_name(skale):
    node = skale.nodes.get_by_name(DEFAULT_NODE_NAME)

    assert list(node.keys()) == FIELDS
    assert node['name'] == DEFAULT_NODE_NAME


def test_get_active_node_ids(skale):
    nodes_number = skale.nodes.get_nodes_number()
    active_node_ids = skale.nodes.get_active_node_ids()

    assert len(active_node_ids) <= nodes_number

    assert isinstance(active_node_ids, list)
    assert len(active_node_ids) > 0

    node = skale.nodes.get(active_node_ids[-1])
    assert list(node.keys()) == FIELDS

    # 0 is active status
    assert all([skale.nodes.get_node_status(node_id) == 0
                for node_id in active_node_ids])


def test_get_active_node_ips(skale):
    nodes_number = skale.nodes.get_nodes_number()

    active_node_ips = skale.nodes.get_active_node_ips()
    assert len(active_node_ips) <= nodes_number

    assert isinstance(active_node_ips, list)

    assert all([Helper.is_valid_ipv4_address(node_ip)
               for node_ip in active_node_ips])


def test_get_active_node_ids_by_address(skale):
    active_node_ids = skale.nodes.get_active_node_ids_by_address(
        skale.wallet.address
    )
    assert isinstance(active_node_ids, list)

    node = skale.nodes.get(active_node_ids[-1])
    assert list(node.keys()) == FIELDS


def test_name_to_id(skale):
    node_name_hash = skale.nodes.name_to_id(DEFAULT_NODE_NAME)
    expected = DEFAULT_NODE_HASH
    assert node_name_hash == expected


def test_is_node_name_available(skale):
    node = skale.nodes.get_by_name(DEFAULT_NODE_NAME)
    unused_name = 'unused_name'
    assert skale.nodes.is_node_name_available(node['name']) is False
    assert skale.nodes.is_node_name_available(unused_name) is True


def test_is_node_ip_available(skale):
    node = skale.nodes.get_by_name(DEFAULT_NODE_NAME)
    node_ip = Helper.ip_from_bytes(node['ip'])

    unused_ip = '123.123.231.123'
    assert skale.nodes.is_node_ip_available(node_ip) is False
    assert skale.nodes.is_node_name_available(unused_ip) is True


def test_node_name_to_index(skale):
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    node_by_id_data = skale.nodes.get(node_id)
    node_by_name_data = skale.nodes.get_by_name(DEFAULT_NODE_NAME)
    assert node_by_id_data == node_by_name_data


def test_get_node_public_key(skale):
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    node_public_key = skale.nodes.get_node_public_key(node_id)
    assert node_public_key == skale.wallet.public_key
