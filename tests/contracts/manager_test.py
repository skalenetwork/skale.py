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

import mock
import web3
from hexbytes import HexBytes

import skale.utils.helper as helper
from skale.utils.constants import GAS
from skale.utils.web3_utils import wait_receipt, private_key_to_public

from tests.utils import generate_random_node_data, generate_random_schain_data


def test_create_node_data_to_bytes(skale):
    ip, public_ip, port, name = generate_random_node_data()
    skale_nonce = helper.generate_nonce()
    pk = private_key_to_public(skale.wallet._private_key)

    bytes_data = skale.manager.create_node_data_to_bytes(
        ip, public_ip, port, name, pk, skale_nonce)
    name_bytes = name.encode()

    assert type(bytes_data) is bytes
    assert bytes_data.find(name_bytes) != -1


def test_create_schain_data_to_bytes(skale):
    type_of_nodes, lifetime_seconds, name = generate_random_schain_data()
    skale_nonce = helper.generate_nonce()

    bytes_data = skale.manager.create_schain_data_to_bytes(
        lifetime_seconds,
        type_of_nodes,
        name,
        skale_nonce
    )
    name_bytes = name.encode()

    assert type(bytes_data) is bytes
    assert bytes_data.find(name_bytes) != -1


def test_get_bounty(skale):
    node_id = 0
    nonce = skale.web3.eth.getTransactionCount(skale.wallet.address)
    gas_price = skale.web3.eth.gasPrice
    contract_address = skale.manager.address
    chain_id = skale.web3.eth.chainId
    expected_txn = {
        'value': 0, 'gasPrice': gas_price, 'chainId': chain_id,
        'gas': GAS['get_bounty'], 'nonce': nonce,
        'to': contract_address,
        'data': (
            '0xee8c4bbf00000000000000000000000000000000000000000000'
            '00000000000000000000'
        )
    }
    exp = skale.web3.eth.account.signTransaction(
        expected_txn, skale.wallet._private_key).rawTransaction
    with mock.patch.object(web3.eth.Eth, 'sendRawTransaction') as send_tx_mock:
        send_tx_mock.return_value = b'hexstring'
        skale.manager.get_bounty(node_id)
        send_tx_mock.assert_called_with(HexBytes(exp))


def test_send_verdict(skale):
    nonce = skale.web3.eth.getTransactionCount(skale.wallet.address)
    gas_price = skale.web3.eth.gasPrice
    contract_address = skale.manager.address
    chain_id = skale.web3.eth.chainId
    expected_txn = {
        'value': 0, 'gasPrice': gas_price, 'chainId': chain_id,
        'gas': 200000, 'nonce': nonce,
        'to': contract_address,
        'data': (
            '0xd77de31c000000000000000000000000000000000000000'
            '0000000000000000000000000000000000000000000000000'
            '000000000000000000000000000000000000007b000000000'
            '0000000000000000000000000000000000000000000000000'
            '0000140000000000000000000000000000000000000000000'
            '00000000000000000000a'
        )
    }
    exp = skale.web3.eth.account.signTransaction(
        expected_txn, skale.wallet._private_key).rawTransaction
    validator_id = 0
    another_node_id = 123
    downtime = 20
    latency = 10
    with mock.patch.object(web3.eth.Eth, 'sendRawTransaction') as send_tx_mock:
        send_tx_mock.return_value = b'hexstring'
        skale.manager.send_verdict(validator_id, another_node_id, downtime,
                                   latency)
        send_tx_mock.assert_called_with(HexBytes(exp))


def test_send_verdicts(skale):
    nonce = skale.web3.eth.getTransactionCount(skale.wallet.address)
    gas_price = skale.web3.eth.gasPrice
    contract_address = skale.manager.address
    chain_id = skale.web3.eth.chainId
    expected_txn = {
        'value': 0, 'gasPrice': gas_price, 'chainId': chain_id,
        'gas': 200000, 'nonce': nonce,
        'to': contract_address,
        'data': ('0x25b2114b000000000000000000000000000000000000000000'
                 '0000000000000000000000000000000000000000000000000000'
                 '0000000000000000000000000000000080000000000000000000'
                 '0000000000000000000000000000000000000000000100000000'
                 '0000000000000000000000000000000000000000000000000000'
                 '0001800000000000000000000000000000000000000000000000'
                 '0000000000000000030000000000000000000000000000000000'
                 '00000000000000000000000000007b0000000000000000000000'
                 '0000000000000000000000000000000000000000e70000000000'
                 '0000000000000000000000000000000000000000000000000001'
                 'c300000000000000000000000000000000000000000000000000'
                 '0000000000000300000000000000000000000000000000000000'
                 '0000000000000000000000000100000000000000000000000000'
                 '0000000000000000000000000000000000000200000000000000'
                 '0000000000000000000000000000000000000000000000000300'
                 '0000000000000000000000000000000000000000000000000000'
                 '0000000003000000000000000000000000000000000000000000'
                 '000000000000000000000a000000000000000000000000000000'
                 '0000000000000000000000000000000014000000000000000000'
                 '000000000000000000000000000000000000000000001e')
    }
    exp = skale.web3.eth.account.signTransaction(
        expected_txn, skale.wallet._private_key).rawTransaction
    validator_id = 0
    another_node_ids = [123, 231, 451]
    downtimes = [1, 2, 3]
    latencies = [10, 20, 30]
    with mock.patch.object(web3.eth.Eth, 'sendRawTransaction') as send_tx_mock:
        send_tx_mock.return_value = b'hexstring'
        skale.manager.send_verdicts(validator_id, another_node_ids, downtimes,
                                    latencies)
        send_tx_mock.assert_called_with(HexBytes(exp))


def test_create_node_delete_node_by_root(skale):
    active_node_ids_before = skale.nodes_data.get_active_node_ids()

    ip, public_ip, port, name = generate_random_node_data()
    res = skale.manager.create_node(ip, port, name)
    receipt = wait_receipt(skale.web3, res['tx'])
    assert receipt['status'] == 1

    active_node_ids_after = skale.nodes_data.get_active_node_ids()
    assert len(active_node_ids_after) == len(active_node_ids_before) + 1

    node_idx = skale.nodes_data.node_name_to_index(name)

    res = skale.manager.delete_node_by_root(node_idx)
    receipt = wait_receipt(skale.web3, res['tx'])
    assert receipt['status'] == 1
    active_node_ids_after = skale.nodes_data.get_active_node_ids()
    assert len(active_node_ids_after) == len(active_node_ids_before)


def test_create_deregister_node(skale):
    # Create node
    active_node_ids_before = skale.nodes_data.get_active_node_ids()

    ip, public_ip, port, name = generate_random_node_data()
    res = skale.manager.create_node(ip, port, name, public_ip)
    receipt = wait_receipt(skale.web3, res['tx'])
    assert receipt['status'] == 1

    active_node_ids_after = skale.nodes_data.get_active_node_ids()
    assert len(active_node_ids_after) == len(active_node_ids_before) + 1

    node_idx = skale.nodes_data.node_name_to_index(name)

    # Deregister node

    res = skale.manager.deregister(node_idx)
    receipt = wait_receipt(skale.web3, res['tx'])
    assert receipt['status'] == 1
    active_node_ids_after = skale.nodes_data.get_active_node_ids()
    assert len(active_node_ids_after) == len(active_node_ids_before)


def test_create_delete_schain(skale):
    schains_ids = skale.schains_data.get_all_schains_ids()

    type_of_nodes, lifetime_seconds, name = generate_random_schain_data()
    price_in_wei = skale.schains.get_schain_price(type_of_nodes,
                                                  lifetime_seconds)
    res = skale.manager.create_schain(lifetime_seconds, type_of_nodes,
                                      price_in_wei, name)
    receipt = wait_receipt(skale.web3, res['tx'])
    assert receipt['status'] == 1

    schains_ids_number_after = skale.schains_data.get_schains_number()
    assert schains_ids_number_after == len(schains_ids) + 1
    schains_ids_after = skale.schains_data.get_all_schains_ids()

    schains_names = [
        skale.schains_data.get(sid)['name']
        for sid in schains_ids_after
    ]
    assert name in schains_names

    res = skale.manager.delete_schain(name)
    receipt = wait_receipt(skale.web3, res['tx'])
    assert receipt['status'] == 1

    schains_ids_number_after = skale.schains_data.get_schains_number()
    assert schains_ids_number_after == len(schains_ids)
    schains_ids_after = skale.schains_data.get_all_schains_ids()

    schains_names = [
        skale.schains_data.get(sid)['name']
        for sid in schains_ids_after
    ]
    assert name not in schains_names
