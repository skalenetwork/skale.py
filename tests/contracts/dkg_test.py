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

import mock
import web3
from hexbytes import HexBytes


def test_broadcast(skale):
    nonce = skale.web3.eth.getTransactionCount(skale.wallet.address)
    gas_price = skale.web3.eth.gasPrice
    contract_address = skale.dkg.address
    chain_id = skale.web3.eth.chainId
    expected_txn = {
        'value': 0, 'gasPrice': gas_price, 'chainId': chain_id,
        'gas': 8000000, 'nonce': nonce,
        'to': contract_address,
        'data': (
            '0x5ee180c165363239666136353938643733323736386637633732366234623632313238350000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000001176616c69646174696f6e2d766563746f7200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000127365637265742d6b65792d636f6e747269620000000000000000000000000000'  # noqa
        )
    }
    group_index = b'e629fa6598d732768f7c726b4b621285'
    node_index = 0
    validation_vector = b'validation-vector'
    secret_key_conribution = b'secret-key-contrib'

    exp = skale.web3.eth.account.signTransaction(
        expected_txn, skale.wallet._private_key).rawTransaction
    with mock.patch.object(web3.eth.Eth, 'sendRawTransaction') as send_tx_mock:
        send_tx_mock.return_value = b'hexstring'
        skale.dkg.broadcast(group_index, node_index,
                            validation_vector, secret_key_conribution)
        send_tx_mock.assert_called_with(HexBytes(exp))


def test_response(skale):
    nonce = skale.web3.eth.getTransactionCount(skale.wallet.address)
    gas_price = skale.web3.eth.gasPrice
    contract_address = skale.dkg.address
    chain_id = skale.web3.eth.chainId
    expected_txn = {
        'value': 0, 'gasPrice': gas_price, 'chainId': chain_id,
        'gas': 8000000, 'nonce': nonce,
        'to': contract_address,
        'data': (
            '0xce86d3ade629fa6598d732768f7c726b4b6212850000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000106d756c7469706c6965645f736861726500000000000000000000000000000000'  # noqa
        )
    }
    group_index = 'e629fa6598d732768f7c726b4b621285'
    from_node_index = 0
    secret_number = 1
    multiplied_share = b'multiplied_share'

    exp = skale.web3.eth.account.signTransaction(
        expected_txn, skale.wallet._private_key).rawTransaction
    with mock.patch.object(web3.eth.Eth, 'sendRawTransaction') as send_tx_mock:
        send_tx_mock.return_value = b'hexstring'
        skale.dkg.response(group_index, from_node_index,
                           secret_number, multiplied_share)
        send_tx_mock.assert_called_with(HexBytes(exp))


def test_allright(skale):
    nonce = skale.web3.eth.getTransactionCount(skale.wallet.address)
    gas_price = skale.web3.eth.gasPrice
    contract_address = skale.dkg.address
    chain_id = skale.web3.eth.chainId
    expected_txn = {
        'value': 0, 'gasPrice': gas_price, 'chainId': chain_id,
        'gas': 1000000, 'nonce': nonce,
        'to': contract_address,
        'data': (
            '0xce5807eee629fa6598d732768f7c726b4b621285000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'  # noqa
        )
    }
    group_index = 'e629fa6598d732768f7c726b4b621285'
    from_node_index = 0

    exp = skale.web3.eth.account.signTransaction(
        expected_txn, skale.wallet._private_key).rawTransaction
    with mock.patch.object(web3.eth.Eth, 'sendRawTransaction') as send_tx_mock:
        send_tx_mock.return_value = b'hexstring'
        skale.dkg.allright(group_index, from_node_index)
        send_tx_mock.assert_called_with(HexBytes(exp))


def test_complaint(skale):
    nonce = skale.web3.eth.getTransactionCount(skale.wallet.address)
    gas_price = skale.web3.eth.gasPrice
    contract_address = skale.dkg.address
    chain_id = skale.web3.eth.chainId
    expected_txn = {
        'value': 0, 'gasPrice': gas_price, 'chainId': chain_id,
        'gas': 1000000, 'nonce': nonce,
        'to': contract_address,
        'data': (
            '0xd76c2c4fe629fa6598d732768f7c726b4b6212850000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'  # noqa
        )
    }
    group_index = 'e629fa6598d732768f7c726b4b621285'
    from_node_index = 0
    to_node_index = 0

    exp = skale.web3.eth.account.signTransaction(
        expected_txn, skale.wallet._private_key).rawTransaction
    with mock.patch.object(web3.eth.Eth, 'sendRawTransaction') as send_tx_mock:
        send_tx_mock.return_value = b'hexstring'
        skale.dkg.complaint(group_index, from_node_index, to_node_index)
        send_tx_mock.assert_called_with(HexBytes(exp))
