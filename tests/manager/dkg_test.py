from unittest import mock
from unittest.mock import Mock

import web3
from hexbytes import HexBytes

from skale.contracts.manager.dkg import G2Point, KeyShare
from skale.utils.helper import split_public_key

SCHAIN_NAME = 'pointed-asellus-australis'
PUBLIC_KEY = '0xfcb3765bdb954ab0672fce731583ad8a94cf05fe63c147f881f8feea18e072d4cad3ec142a65de66a1d50e4fc34a7841c5488ccb55d02cf86013208c17517d64'  # noqa


def assert_transaction_data_in_mock(expected_txn, send_tx_mock):
    assert expected_txn['data'][2:] in HexBytes(send_tx_mock.call_args[0][0]).hex()


def test_response(skale):
    nonce = skale.web3.eth.get_transaction_count(skale.wallet.address)
    contract_address = skale.dkg.address
    chain_id = skale.web3.eth.chain_id
    gas_limit = 11000000
    expected_txn = {
        'value': 0,
        'gasPrice': skale.web3.eth.gas_price,
        'chainId': chain_id,
        'gas': gas_limit,
        'nonce': nonce,
        'type': 1,
        'to': contract_address,
        'data': (
            '0x587e22fee332bac19e758fe13db6129827da76846b8c6d26f1e70385d3f0afc0299e3db9000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000024000000000000000000000000000000000000000000000000000000000000003e0000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000001fcb3765bdb954ab0672fce731583ad8a94cf05fe63c147f881f8feea18e072d4cad3ec142a65de66a1d50e4fc34a7841c5488ccb55d02cf86013208c17517d64e332bac19e758fe13db6129827da76846b8c6d26f1e70385d3f0afc0299e3db9'  # noqa
        ),
    }
    from_node_index = 0
    group_index = skale.schains.name_to_id(SCHAIN_NAME)
    share = group_index  # not an invariant, only a mock
    secret_number = 1
    multiplied_share = G2Point((1, 2), (3, 4))
    verification_vector = [G2Point((1, 2), (3, 4)) for i in range(0, 3)]
    verification_vector_mult = [G2Point((1, 2), (3, 4)) for i in range(0, 3)]
    secret_key_contribution = [KeyShare(split_public_key(PUBLIC_KEY), share)]

    with mock.patch.object(
        skale.dkg.contract.functions.preResponse, 'call', new=Mock(return_value=[])
    ):
        with mock.patch.object(web3.eth.Eth, 'send_raw_transaction') as send_tx_mock:
            send_tx_mock.return_value = b'hexstring'
            skale.dkg.pre_response(
                group_index=group_index,
                from_node_index=from_node_index,
                verification_vector=verification_vector,
                verification_vector_mult=verification_vector_mult,
                secret_key_contribution=secret_key_contribution,
                wait_for=False,
                gas_limit=gas_limit,
            )
            send_tx_mock.assert_called_with(mock.ANY)
            assert_transaction_data_in_mock(expected_txn, send_tx_mock)

    expected_txn = {
        'value': 0,
        'gasPrice': skale.web3.eth.gas_price,
        'chainId': chain_id,
        'gas': gas_limit,
        'nonce': nonce,
        'to': contract_address,
        'type': 1,
        'data': (
            '0x6ef89763e332bac19e758fe13db6129827da76846b8c6d26f1e70385d3f0afc0299e3db9000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000004'  # noqa
        ),
    }

    with mock.patch.object(
        skale.dkg.contract.functions.response, 'call', new=Mock(return_value=[])
    ):
        with mock.patch.object(web3.eth.Eth, 'send_raw_transaction') as send_tx_mock:
            send_tx_mock.return_value = b'hexstring'
            skale.dkg.response(
                group_index=group_index,
                from_node_index=from_node_index,
                secret_number=secret_number,
                multiplied_share=multiplied_share,
                wait_for=False,
                gas_limit=gas_limit,
            )
            send_tx_mock.assert_called_with(mock.ANY)
            assert_transaction_data_in_mock(expected_txn, send_tx_mock)


def test_alright(skale):
    nonce = skale.web3.eth.get_transaction_count(skale.wallet.address)
    contract_address = skale.dkg.address
    chain_id = skale.web3.eth.chain_id
    gas_limit = 10000000
    expected_txn = {
        'value': 0,
        'gasPrice': skale.web3.eth.gas_price,
        'chainId': chain_id,
        'gas': gas_limit,
        'nonce': nonce,
        'type': 1,
        'to': contract_address,
        'data': (
            '0xb9799682e332bac19e758fe13db6129827da76846b8c6d26f1e70385d3f0afc0299e3db90000000000000000000000000000000000000000000000000000000000000000'  # noqa
        ),
    }
    group_index = skale.schains.name_to_id(SCHAIN_NAME)
    from_node_index = 0

    with mock.patch.object(skale.dkg.contract.functions.alright, 'call', new=Mock(return_value=[])):
        with mock.patch.object(web3.eth.Eth, 'send_raw_transaction') as send_tx_mock:
            send_tx_mock.return_value = b'hexstring'
            skale.dkg.alright(group_index, from_node_index, wait_for=False, gas_limit=gas_limit)
            assert_transaction_data_in_mock(expected_txn, send_tx_mock)


def test_complaint(skale):
    nonce = skale.web3.eth.get_transaction_count(skale.wallet.address)
    contract_address = skale.dkg.address
    chain_id = skale.web3.eth.chain_id
    gas_limit = 8000000
    expected_txn = {
        'value': 0,
        'gasPrice': skale.web3.eth.gas_price,
        'chainId': chain_id,
        'gas': gas_limit,
        'nonce': nonce,
        'to': contract_address,
        'type': 1,
        'data': (
            '0xd76c2c4fe332bac19e758fe13db6129827da76846b8c6d26f1e70385d3f0afc0299e3db900000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'  # noqa
        ),
    }
    group_index = skale.schains.name_to_id(SCHAIN_NAME)
    from_node_index = 0
    to_node_index = 0

    with mock.patch.object(
        skale.dkg.contract.functions.complaint, 'call', new=Mock(return_value=[])
    ):
        with mock.patch.object(web3.eth.Eth, 'send_raw_transaction') as send_tx_mock:
            send_tx_mock.return_value = b'hexstring'
            skale.dkg.complaint(
                group_index, from_node_index, to_node_index, wait_for=False, gas_limit=gas_limit
            )
            assert_transaction_data_in_mock(expected_txn, send_tx_mock)


def test_complaint_bad_data(skale):
    nonce = skale.web3.eth.get_transaction_count(skale.wallet.address)
    contract_address = skale.dkg.address
    chain_id = skale.web3.eth.chain_id
    gas_limit = 8000000
    expected_txn = {
        'value': 0,
        'gasPrice': skale.web3.eth.gas_price,
        'chainId': chain_id,
        'gas': gas_limit,
        'nonce': nonce,
        'to': contract_address,
        'type': 1,
        'data': (
            '0xd76c2c4fe332bac19e758fe13db6129827da76846b8c6d26f1e70385d3f0afc0299e3db900000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'  # noqa
        ),
    }
    group_index = skale.schains.name_to_id(SCHAIN_NAME)
    from_node_index = 0
    to_node_index = 0

    with mock.patch.object(
        skale.dkg.contract.functions.complaintBadData, 'call', new=Mock(return_value=[])
    ):
        with mock.patch.object(web3.eth.Eth, 'send_raw_transaction') as send_tx_mock:
            send_tx_mock.return_value = b'hexstring'
            skale.dkg.complaint(
                group_index, from_node_index, to_node_index, wait_for=False, gas_limit=gas_limit
            )
            assert_transaction_data_in_mock(expected_txn, send_tx_mock)


def test_is_last_dkg_successful(skale, schain):
    group_index = skale.web3.keccak(text=schain)
    assert not skale.dkg.is_last_dkg_successful(group_index)


def test_channel_opened(skale, schain):
    group_index = skale.web3.keccak(text=schain)
    assert skale.dkg.is_channel_opened(group_index)


def test_broadcast_possible(skale, nodes, schain, node_wallets):
    group_index = skale.web3.keccak(text=schain)
    node_id, *_ = nodes
    wallet, *_ = node_wallets
    assert skale.dkg.is_broadcast_possible(group_index, node_id, wallet.address)


def test_alright_possible(skale, nodes, schain, node_wallets):
    group_index = skale.web3.keccak(text=schain)
    node_id, *_ = nodes
    wallet, *_ = node_wallets
    assert not skale.dkg.is_alright_possible(group_index, node_id, wallet.address)


def test_pre_response_possible(skale, nodes, schain, node_wallets):
    group_index = skale.web3.keccak(text=schain)
    node_id, *_ = nodes
    wallet, *_ = node_wallets
    assert not skale.dkg.is_pre_response_possible(group_index, node_id, wallet.address)


def test_response_possible(skale, nodes, schain, node_wallets):
    group_index = skale.web3.keccak(text=schain)
    node_id, *_ = nodes
    wallet, *_ = node_wallets
    assert not skale.dkg.is_response_possible(group_index, node_id, wallet.address)


def test_everyone_broadcasted(skale, schain):
    group_index = skale.web3.keccak(text=schain)
    assert not skale.dkg.is_everyone_broadcasted(group_index, skale.wallet.address)


def test_number_of_completed(skale, schain):
    group_index = skale.web3.keccak(text=schain)
    assert skale.dkg.get_number_of_completed(group_index) == 0


def test_channel_started_time(skale, schain):
    group_index = skale.web3.keccak(text=schain)
    assert skale.dkg.get_channel_started_time(group_index) != 0


def test_complaint_started_time(skale, schain):
    group_index = skale.web3.keccak(text=schain)
    assert skale.dkg.get_complaint_started_time(group_index) == 0


def test_alright_started_time(skale, schain):
    group_index = skale.web3.keccak(text=schain)
    assert skale.dkg.get_alright_started_time(group_index) == 0


def test_get_complaint_data(skale, schain):
    group_index = skale.web3.keccak(text=schain)
    assert skale.dkg.get_complaint_data(group_index) != [0, 0]


def test_time_of_last_successful_dkg(skale, schain):
    group_index = skale.web3.keccak(text=schain)
    assert skale.dkg.get_time_of_last_successful_dkg(group_index) == 0
