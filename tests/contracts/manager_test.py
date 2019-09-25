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
""" SKALE manager test """

import pytest

import skale.utils.helper as Helper
from tests.constants import DEFAULT_NODE_NAME
from tests.utils import generate_random_node_data, generate_random_schain_data


def test_create_node_data_to_bytes(skale, wallet):
    ip, public_ip, port, name = generate_random_node_data()
    skale_nonce = Helper.generate_nonce()
    pk = Helper.private_key_to_public(wallet['private_key'])

    bytes_data = skale.manager.create_node_data_to_bytes(
        ip, public_ip, port, name, pk, skale_nonce)
    name_bytes = name.encode()

    assert type(bytes_data) is bytes
    assert bytes_data.find(name_bytes) != -1


def test_create_schain_data_to_bytes(skale):
    type_of_nodes, lifetime_seconds, name = generate_random_schain_data()
    skale_nonce = Helper.generate_nonce()

    bytes_data = skale.manager.create_schain_data_to_bytes(
        lifetime_seconds,
        type_of_nodes,
        name,
        skale_nonce
    )
    name_bytes = name.encode()

    assert type(bytes_data) is bytes
    assert bytes_data.find(name_bytes) != -1


def test_get_bounty(skale_wallet_with_nodes_schain):
    skale, wallet = skale_wallet_with_nodes_schain
    node_id = skale.nodes_data.node_name_to_index(DEFAULT_NODE_NAME)
    res = skale.manager.get_bounty(node_id, wallet)
    receipt = Helper.await_receipt(skale.web3, res['tx'])
    # assert receipt['status'] == 1  # todo: we couldn't test it here
    # todo: check account balance before and after


def test_send_verdict(skale, wallet):
    pass  # todo!


@pytest.mark.skip('Broken test. Should be fixed')
def test_create_deregister_node(skale_wallet_with_nodes_schain):

    skale, wallet = skale_wallet_with_nodes_schain
    active_node_ids_before = skale.nodes_data.get_active_node_ids()

    ip, public_ip, port, name = generate_random_node_data()
    res = skale.manager.create_node(ip, port, name, wallet, public_ip)
    receipt = Helper.await_receipt(skale.web3, res['tx'])
    assert receipt['status'] == 1

    active_node_ids_after = skale.nodes_data.get_active_node_ids()
    assert len(active_node_ids_after) == len(active_node_ids_before) + 1

    node_idx = skale.nodes_data.node_name_to_index(name)

    res = skale.manager.deregister(node_idx, wallet)
    receipt = Helper.await_receipt(skale.web3, res['tx'])
    assert receipt['status'] == 1

    active_node_ids_after = skale.nodes_data.get_active_node_ids()
    assert len(active_node_ids_after) == len(active_node_ids_before)


def test_create_delete_schain(skale_wallet_with_nodes_schain):
    skale, wallet = skale_wallet_with_nodes_schain
    schains_ids = skale.schains_data.get_all_schains_ids()

    # create schain
    type_of_nodes, lifetime_seconds, name = generate_random_schain_data()
    price_in_wei = skale.schains.get_schain_price(type_of_nodes, lifetime_seconds)
    res = skale.manager.create_schain(lifetime_seconds, type_of_nodes,
                                      price_in_wei, name, wallet)
    receipt = Helper.await_receipt(skale.web3, res['tx'])

    assert receipt['status'] == 1

    schains_ids_after = skale.schains_data.get_all_schains_ids()
    assert len(schains_ids_after) == len(schains_ids) + 1

    # remove it
    res = skale.manager.delete_schain(name, wallet)
    receipt = Helper.await_receipt(skale.web3, res['tx'])
    assert receipt['status'] == 1

    schains_ids_after = skale.schains_data.get_all_schains_ids()
    assert len(schains_ids_after) == len(schains_ids)
