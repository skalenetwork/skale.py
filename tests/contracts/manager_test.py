""" SKALE manager test """

import mock
import pytest
import web3
from hexbytes import HexBytes

import skale.utils.helper as helper
from skale.utils.constants import GAS
from skale.utils.web3_utils import (private_key_to_public, TransactionFailedError)

from tests.utils import generate_random_node_data, generate_random_schain_data
from tests.prepare_data import clean_and_restart


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
    contract_address = skale.manager.address
    chain_id = skale.web3.eth.chainId
    expected_txn = {
        'value': 0, 'gasPrice': skale.gas_price, 'chainId': chain_id,
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
    contract_address = skale.manager.address
    chain_id = skale.web3.eth.chainId
    expected_txn = {
        'value': 0, 'gasPrice': skale.gas_price, 'chainId': chain_id,
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
    contract_address = skale.manager.address
    chain_id = skale.web3.eth.chainId
    expected_txn = {
        'value': 0, 'gasPrice': skale.gas_price, 'chainId': chain_id,
        'gas': 500000, 'nonce': nonce,
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
    tx_res = skale.manager.create_node(ip, port, name, wait_for=True)
    assert tx_res.receipt['status'] == 1

    active_node_ids_after = skale.nodes_data.get_active_node_ids()
    assert len(active_node_ids_after) == len(active_node_ids_before) + 1

    node_idx = skale.nodes_data.node_name_to_index(name)

    tx_res = skale.manager.delete_node_by_root(node_idx, wait_for=True)
    assert tx_res.receipt['status'] == 1
    active_node_ids_after = skale.nodes_data.get_active_node_ids()
    assert len(active_node_ids_after) == len(active_node_ids_before)


def test_create_deregister_node(skale):
    # Create node
    active_node_ids_before = skale.nodes_data.get_active_node_ids()

    ip, public_ip, port, name = generate_random_node_data()
    tx_res = skale.manager.create_node(ip, port, name, public_ip, wait_for=True)
    assert tx_res.receipt['status'] == 1

    active_node_ids_after = skale.nodes_data.get_active_node_ids()
    assert len(active_node_ids_after) == len(active_node_ids_before) + 1

    node_idx = skale.nodes_data.node_name_to_index(name)

    # Deregister node

    tx_res = skale.manager.deregister(node_idx, wait_for=True)
    assert tx_res.receipt['status'] == 1
    active_node_ids_after = skale.nodes_data.get_active_node_ids()
    assert len(active_node_ids_after) == len(active_node_ids_before)


def test_create_delete_schain(skale):
    schains_ids = skale.schains_data.get_all_schains_ids()

    type_of_nodes, lifetime_seconds, name = generate_random_schain_data()
    price_in_wei = skale.schains.get_schain_price(type_of_nodes,
                                                  lifetime_seconds)
    tx_res = skale.manager.create_schain(lifetime_seconds, type_of_nodes,
                                         price_in_wei, name, wait_for=True)
    assert tx_res.receipt['status'] == 1

    schains_ids_number_after = skale.schains_data.get_schains_number()
    assert schains_ids_number_after == len(schains_ids) + 1
    schains_ids_after = skale.schains_data.get_all_schains_ids()

    schains_names = [
        skale.schains_data.get(sid)['name']
        for sid in schains_ids_after
    ]
    assert name in schains_names

    tx_res = skale.manager.delete_schain(name, wait_for=True)
    assert tx_res.receipt['status'] == 1

    schains_ids_number_after = skale.schains_data.get_schains_number()
    assert schains_ids_number_after == len(schains_ids)
    schains_ids_after = skale.schains_data.get_all_schains_ids()

    schains_names = [
        skale.schains_data.get(sid)['name']
        for sid in schains_ids_after
    ]
    assert name not in schains_names


def test_create_delete_default_schain(skale):
    schains_ids = skale.schains_data.get_all_schains_ids()
    name = 'default-schain'
    tx_res = skale.manager.create_default_schain(name)
    assert tx_res.receipt['status'] == 1

    schains_ids_number_after = skale.schains_data.get_schains_number()
    assert schains_ids_number_after == len(schains_ids) + 1
    schains_ids_after = skale.schains_data.get_all_schains_ids()

    schains_names = [
        skale.schains_data.get(sid)['name']
        for sid in schains_ids_after
    ]
    assert name in schains_names

    tx_res = skale.manager.delete_schain(name, wait_for=True)
    assert tx_res.receipt['status'] == 1

    schains_ids_number_after = skale.schains_data.get_schains_number()
    assert schains_ids_number_after == len(schains_ids)
    schains_ids_after = skale.schains_data.get_all_schains_ids()

    schains_names = [
        skale.schains_data.get(sid)['name']
        for sid in schains_ids_after
    ]
    assert name not in schains_names


def test_create_node_status_0(skale):
    ip, public_ip, port, name = generate_random_node_data()
    with mock.patch.object(web3.eth.Eth, 'sendRawTransaction') as send_tx_mock:
        send_tx_mock.return_value = b'hexstring'
        with mock.patch(
            'skale.contracts.base_contract.wait_for_receipt_by_blocks',
            return_value={'status': 0}
        ):
            with pytest.raises(TransactionFailedError):
                skale.manager.create_node(ip, port, name, wait_for=True)


def test_empty_node_exit(skale):
    ip, public_ip, port, name = generate_random_node_data()
    skale.manager.create_node(ip, port, name, public_ip, wait_for=True)
    node_idx = skale.nodes_data.node_name_to_index(name)
    tx_res = skale.manager.node_exit(node_idx, wait_for=True)
    assert tx_res.receipt['status'] == 1
    assert skale.nodes_data.get_node_status(node_idx) == 2


def test_one_schain_node_exit(skale):
    schains_ids = skale.schains_data.get_all_schains_ids()
    schain_name = skale.schains_data.get(schains_ids[0])['name']
    exit_node_id = skale.schains_data.get_node_ids_for_schain(schain_name)[0]
    with pytest.raises(ValueError):
        skale.manager.node_exit(exit_node_id, wait_for=True)
    ip, public_ip, port, name = generate_random_node_data()
    skale.manager.create_node(ip, port, name, public_ip, wait_for=True)
    new_node_id = skale.nodes_data.node_name_to_index(name)
    tx_res = skale.manager.node_exit(exit_node_id, wait_for=True)
    assert tx_res.receipt['status'] == 1
    assert skale.nodes_data.get_node_status(exit_node_id) == 2

    assert len(skale.schains_data.get_schain_ids_for_node(exit_node_id)) == 0
    assert len(skale.schains_data.get_schain_ids_for_node(new_node_id)) == 1

    history = skale.schains_data.get_leaving_history(exit_node_id)
    assert len(history) == 1
    assert history[0][1]
    assert skale.schains_data.get(history[0][0])['name'] == schain_name

    clean_and_restart(skale)


def test_get_rotation(skale):
    schains_ids = skale.schains_data.get_all_schains_ids()
    schain_name = skale.schains_data.get(schains_ids[0])['name']
    exit_node_id = skale.schains_data.get_node_ids_for_schain(schain_name)[0]

    ip, public_ip, port, name = generate_random_node_data()
    skale.manager.create_node(ip, port, name, public_ip, wait_for=True)
    new_node_id = skale.nodes_data.node_name_to_index(name)
    skale.manager.node_exit(exit_node_id, wait_for=True)
    rotation = skale.schains_data.get_rotation(schain_name)
    history = skale.schains_data.get_leaving_history(exit_node_id)
    assert rotation['leaving_node'] == exit_node_id
    assert rotation['new_node'] == new_node_id
    assert rotation['finish_ts'] == history[0][1]

    last_rotation = skale.schains_data.get_last_rotation_id(schain_name)
    assert rotation['rotation_id'] == last_rotation

    clean_and_restart(skale)
