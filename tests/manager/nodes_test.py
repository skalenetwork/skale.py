"""SKALE node test"""

import random
import socket
import string
from datetime import datetime

import pytest
from eth_keys import keys
from web3 import Web3

import skale.utils.helper as Helper
from skale.contracts.manager.nodes import FIELDS, NodeStatus
from skale.utils.contracts_provision import DEFAULT_DOMAIN_NAME
from skale.utils.contracts_provision.utils import generate_random_ip
from skale.utils.exceptions import InvalidNodeIdError
from tests.constants import DEFAULT_NODE_NAME, NOT_EXISTING_ID


def test_get_raw_not_exist(skale):
    with pytest.raises(InvalidNodeIdError):
        skale.nodes._Nodes__get_raw(NOT_EXISTING_ID)


def public_key_from_private(key):
    pr_bytes = Web3.to_bytes(hexstr=key)
    return keys.PrivateKey(pr_bytes)


def test_get(skale, nodes, node_wallets):
    node = skale.nodes.get_by_name(DEFAULT_NODE_NAME)
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    node_by_id = skale.nodes.get(node_id)
    assert list(node.keys()) == FIELDS
    assert [k for k, v in node.items() if v is None] == []
    assert node_by_id['name'] == DEFAULT_NODE_NAME
    socket.inet_ntoa(node_by_id['ip'])
    socket.inet_ntoa(node_by_id['publicIP'])

    assert node_by_id['publicKey'] == node_wallets[0].public_key

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


def test_wrong_node_id(skale):
    with pytest.raises(InvalidNodeIdError):
        skale.nodes.get_node_status(NOT_EXISTING_ID)

    with pytest.raises(InvalidNodeIdError):
        skale.nodes.get_node_finish_time(NOT_EXISTING_ID)


def test_get_active_node_ids(skale, nodes):
    nodes_number = skale.nodes.get_nodes_number()
    active_node_ids = skale.nodes.get_active_node_ids()

    assert len(active_node_ids) <= nodes_number

    assert isinstance(active_node_ids, list)
    assert len(active_node_ids) > 0

    node = skale.nodes.get(active_node_ids[-1])
    assert list(node.keys()) == FIELDS

    # 0 is active status
    assert all([skale.nodes.get_node_status(node_id) == 0 for node_id in active_node_ids])


def test_get_active_node_ips(skale, nodes):
    nodes_number = skale.nodes.get_nodes_number()

    active_node_ips = skale.nodes.get_active_node_ips()
    assert len(active_node_ips) <= nodes_number

    assert isinstance(active_node_ips, list)

    assert all([Helper.is_valid_ipv4_address(node_ip) for node_ip in active_node_ips])


def test_is_node_name_available(skale, nodes):
    node = skale.nodes.get_by_name(DEFAULT_NODE_NAME)
    unused_name = 'unused_name'
    assert skale.nodes.is_node_name_available(node['name']) is False
    assert skale.nodes.is_node_name_available(unused_name) is True


def test_is_node_ip_available(skale, nodes):
    node = skale.nodes.get_by_name(DEFAULT_NODE_NAME)
    node_ip = Helper.ip_from_bytes(node['ip'])

    unused_ip = '123.123.231.123'
    assert skale.nodes.is_node_ip_available(node_ip) is False
    assert skale.nodes.is_node_name_available(unused_ip) is True


def test_node_name_to_index(skale, nodes):
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    node_by_id_data = skale.nodes.get(node_id)
    node_by_name_data = skale.nodes.get_by_name(DEFAULT_NODE_NAME)
    assert node_by_id_data == node_by_name_data


def test_get_node_public_key(skale, nodes, node_wallets):
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    node_public_key = skale.nodes.get_node_public_key(node_id)
    assert node_public_key == node_wallets[0].public_key

    with pytest.raises(InvalidNodeIdError):
        skale.nodes.get_node_public_key(NOT_EXISTING_ID)


def test_node_in_maintenance(skale, nodes):
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    assert skale.nodes.get_node_status(node_id) == NodeStatus.ACTIVE.value

    try:
        skale.nodes.set_node_in_maintenance(node_id)
        assert skale.nodes.get_node_status(node_id) == NodeStatus.IN_MAINTENANCE.value
    finally:
        skale.nodes.remove_node_from_in_maintenance(node_id)
    assert skale.nodes.get_node_status(node_id) == NodeStatus.ACTIVE.value


def test_set_domain_name(skale, nodes):
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    node = skale.nodes.get(node_id)
    random_domain = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    assert node['domain_name'] != random_domain

    skale.nodes.set_domain_name(node_id, random_domain)

    node = skale.nodes.get(node_id)
    assert node['domain_name'] == random_domain

    skale.nodes.set_domain_name(node_id, DEFAULT_DOMAIN_NAME)


def test_get_domain_name(skale, nodes):
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    node = skale.nodes.get(node_id)
    assert node['domain_name'] == DEFAULT_DOMAIN_NAME


def test_get_node_next_reward_date(skale, nodes):
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    next_reward_date_ts = skale.nodes.get_node_next_reward_date(node_id)
    next_reward_date = datetime.utcfromtimestamp(next_reward_date_ts)
    present = datetime.now()
    assert next_reward_date > present


def test_change_ip(skale, nodes):
    node_id, _ = nodes
    old_ip = skale.nodes.get(node_id)['ip']

    new_ip = Helper.ip_to_bytes(generate_random_ip())

    skale.nodes.change_ip(node_id, new_ip, new_ip)
    data = skale.nodes.get(node_id)
    assert data['ip'] == new_ip
    assert data['publicIP'] == new_ip

    skale.nodes.change_ip(node_id, old_ip, old_ip)
    data = skale.nodes.get(node_id)
    assert data['ip'] == old_ip
    assert data['publicIP'] == old_ip


def test_get_last_change_ip_time(skale, nodes):
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    new_ip = Helper.ip_to_bytes(generate_random_ip())
    tx = skale.nodes.change_ip(node_id, new_ip, new_ip, wait_for=True, confirmation_blocks=5)
    change_timestamp = skale.nodes.get_last_change_ip_time(node_id)
    block = skale.web3.eth.get_block(tx.receipt.blockNumber)
    assert change_timestamp == block.timestamp
