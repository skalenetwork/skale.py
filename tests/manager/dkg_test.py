import mock
import web3
from mock import Mock
from hexbytes import HexBytes

from skale.contracts.manager.dkg import G2Point, KeyShare
from tests.constants import DEFAULT_SCHAIN_NAME


def test_broadcast(skale):
    nonce = skale.web3.eth.getTransactionCount(skale.wallet.address)
    contract_address = skale.dkg.address
    chain_id = skale.web3.eth.chainId
    gas_limit = 8000000
    expected_txn = {
        'value': 0, 'gasPrice': skale.web3.eth.gasPrice * 2, 'chainId': chain_id,
        'gas': gas_limit, 'nonce': nonce,
        'type': 1,
        'to': contract_address,
        'data': (
            '0x7d93019b653632396661363539386437333237363866376337323662346236323132383500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000022000000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000001f925c203a30ec6cad5a263db3efab7ed4c1fd74c8688167e10a5a22e15ab5018d8553df0ac54ea105a3d21845e5660bc3d4e7c82e7af1daa3baad393b15214673131310000000000000000000000000000000000000000000000000000000000'  # noqa
        )
    }
    print(expected_txn)
    group_index = b'e629fa6598d732768f7c726b4b621285'
    node_index = 0

    verification_vector = [G2Point(1, 2, 3, 4).tuple for i in range(0, 3)]
    secret_key_contribution = [KeyShare(skale.wallet.public_key, b'111').tuple]

    exp = skale.web3.eth.account.signTransaction(
        expected_txn, skale.wallet._private_key).rawTransaction
    with mock.patch.object(skale.dkg.contract.functions.broadcast, 'call',
                           new=Mock(return_value=[])):
        with mock.patch.object(web3.eth.Eth, 'sendRawTransaction') as send_tx_mock:
            send_tx_mock.return_value = b'hexstring'
            skale.dkg.broadcast(group_index, node_index, verification_vector,
                                secret_key_contribution,
                                gas_limit=gas_limit,
                                wait_for=False)
            print(send_tx_mock.call_args)
            send_tx_mock.assert_called_with(HexBytes(exp))


def test_response(skale):
    nonce = skale.web3.eth.getTransactionCount(skale.wallet.address)
    contract_address = skale.dkg.address
    chain_id = skale.web3.eth.chainId
    gas_limit = 11000000
    expected_txn = {
        'value': 0, 'gasPrice': skale.web3.eth.gasPrice * 2, 'chainId': chain_id,
        'gas': gas_limit, 'nonce': nonce,
        'type': 1,
        'to': contract_address,
        'data': (
            '0x587e22fee629fa6598d732768f7c726b4b62128500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000024000000000000000000000000000000000000000000000000000000000000003e0000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000001f925c203a30ec6cad5a263db3efab7ed4c1fd74c8688167e10a5a22e15ab5018d8553df0ac54ea105a3d21845e5660bc3d4e7c82e7af1daa3baad393b15214673131310000000000000000000000000000000000000000000000000000000000'  # noqa
        )
    }
    group_index = 'e629fa6598d732768f7c726b4b621285'
    from_node_index = 0
    secret_number = 1
    multiplied_share = G2Point(1, 2, 3, 4).tuple
    verification_vector = [G2Point(1, 2, 3, 4).tuple for i in range(0, 3)]
    verification_vector_mult = [G2Point(1, 2, 3, 4).tuple for i in range(0, 3)]
    secret_key_contribution = [KeyShare(skale.wallet.public_key, b'111').tuple]

    exp = skale.web3.eth.account.signTransaction(
        expected_txn, skale.wallet._private_key).rawTransaction

    with mock.patch.object(skale.dkg.contract.functions.preResponse, 'call',
                           new=Mock(return_value=[])):
        with mock.patch.object(web3.eth.Eth, 'sendRawTransaction') as send_tx_mock:
            send_tx_mock.return_value = b'hexstring'
            skale.dkg.pre_response(
                group_index=group_index,
                from_node_index=from_node_index,
                verification_vector=verification_vector,
                verification_vector_mult=verification_vector_mult,
                secret_key_contribution=secret_key_contribution,
                wait_for=False,
                gas_limit=gas_limit
            )
            send_tx_mock.assert_called_with(HexBytes(exp))

    expected_txn = {
        'value': 0, 'gasPrice': skale.web3.eth.gasPrice * 2, 'chainId': chain_id,
        'gas': gas_limit, 'nonce': nonce,
        'to': contract_address,
        'type': 1,
        'data': (
            '0x6ef89763e629fa6598d732768f7c726b4b62128500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000004'  # noqa
        )
    }
    exp = skale.web3.eth.account.signTransaction(
        expected_txn, skale.wallet._private_key).rawTransaction

    with mock.patch.object(skale.dkg.contract.functions.response, 'call',
                           new=Mock(return_value=[])):
        with mock.patch.object(web3.eth.Eth, 'sendRawTransaction') as send_tx_mock:
            send_tx_mock.return_value = b'hexstring'
            skale.dkg.response(
                group_index=group_index,
                from_node_index=from_node_index,
                secret_number=secret_number,
                multiplied_share=multiplied_share,
                wait_for=False,
                gas_limit=gas_limit
            )
            send_tx_mock.assert_called_with(HexBytes(exp))


def test_alright(skale):
    nonce = skale.web3.eth.getTransactionCount(skale.wallet.address)
    contract_address = skale.dkg.address
    chain_id = skale.web3.eth.chainId
    gas_limit = 10000000
    expected_txn = {
        'value': 0, 'gasPrice': skale.web3.eth.gasPrice * 2, 'chainId': chain_id,
        'gas': gas_limit, 'nonce': nonce,
        'type': 1,
        'to': contract_address,
        'data': (
            '0xb9799682e629fa6598d732768f7c726b4b621285000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'  # noqa
        )
    }
    group_index = 'e629fa6598d732768f7c726b4b621285'
    from_node_index = 0

    exp = skale.web3.eth.account.signTransaction(
        expected_txn, skale.wallet._private_key).rawTransaction

    with mock.patch.object(skale.dkg.contract.functions.alright,
                           'call', new=Mock(return_value=[])):
        with mock.patch.object(web3.eth.Eth, 'sendRawTransaction') as send_tx_mock:
            send_tx_mock.return_value = b'hexstring'
            skale.dkg.alright(group_index, from_node_index,
                              wait_for=False,
                              gas_limit=gas_limit)
            send_tx_mock.assert_called_with(HexBytes(exp))


def test_complaint(skale):
    nonce = skale.web3.eth.getTransactionCount(skale.wallet.address)
    contract_address = skale.dkg.address
    chain_id = skale.web3.eth.chainId
    gas_limit = 8000000
    expected_txn = {
        'value': 0, 'gasPrice': skale.web3.eth.gasPrice * 2, 'chainId': chain_id,
        'gas': gas_limit, 'nonce': nonce,
        'to': contract_address,
        'type': 1,
        'data': (
            '0xd76c2c4fe629fa6598d732768f7c726b4b6212850000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'  # noqa
        )
    }
    group_index = 'e629fa6598d732768f7c726b4b621285'
    from_node_index = 0
    to_node_index = 0

    exp = skale.web3.eth.account.signTransaction(
        expected_txn, skale.wallet._private_key).rawTransaction
    with mock.patch.object(skale.dkg.contract.functions.complaint,
                           'call', new=Mock(return_value=[])):
        with mock.patch.object(web3.eth.Eth, 'sendRawTransaction') as send_tx_mock:
            send_tx_mock.return_value = b'hexstring'
            skale.dkg.complaint(group_index, from_node_index, to_node_index,
                                wait_for=False,
                                gas_limit=gas_limit)
            send_tx_mock.assert_called_with(HexBytes(exp))


def test_complaint_bad_data(skale):
    nonce = skale.web3.eth.getTransactionCount(skale.wallet.address)
    contract_address = skale.dkg.address
    chain_id = skale.web3.eth.chainId
    gas_limit = 8000000
    expected_txn = {
        'value': 0, 'gasPrice': skale.web3.eth.gasPrice * 2, 'chainId': chain_id,
        'gas': gas_limit, 'nonce': nonce,
        'to': contract_address,
        'type': 1,
        'data': (
            '0xd76c2c4fe629fa6598d732768f7c726b4b6212850000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'  # noqa
        )
    }
    group_index = 'e629fa6598d732768f7c726b4b621285'
    from_node_index = 0
    to_node_index = 0

    exp = skale.web3.eth.account.signTransaction(
        expected_txn, skale.wallet._private_key).rawTransaction
    with mock.patch.object(skale.dkg.contract.functions.complaintBadData,
                           'call', new=Mock(return_value=[])):
        with mock.patch.object(web3.eth.Eth, 'sendRawTransaction') as send_tx_mock:
            send_tx_mock.return_value = b'hexstring'
            skale.dkg.complaint(group_index, from_node_index, to_node_index,
                                wait_for=False,
                                skip_dry_run=True,
                                gas_limit=gas_limit)
            send_tx_mock.assert_called_with(HexBytes(exp))


def test_is_last_dkg_successful(skale):
    group_index = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    assert not skale.dkg.is_last_dkg_successful(group_index)


def test_channel_opened(skale):
    group_index = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    assert skale.dkg.is_channel_opened(group_index)


def test_broadcast_possible(skale):
    group_index = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    node_id = 0
    assert skale.dkg.is_broadcast_possible(group_index, node_id, skale.wallet.address)


def test_alright_possible(skale):
    group_index = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    node_id = 0
    assert not skale.dkg.is_alright_possible(group_index, node_id, skale.wallet.address)


def test_pre_response_possible(skale):
    group_index = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    node_id = 0
    assert not skale.dkg.is_pre_response_possible(group_index, node_id, skale.wallet.address)


def test_response_possible(skale):
    group_index = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    node_id = 0
    assert not skale.dkg.is_response_possible(group_index, node_id, skale.wallet.address)


def test_everyone_broadcasted(skale):
    group_index = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    assert not skale.dkg.is_everyone_broadcasted(group_index, skale.wallet.address)


def test_number_of_completed(skale):
    group_index = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    assert skale.dkg.get_number_of_completed(group_index) == 0


def test_channel_started_time(skale):
    group_index = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    assert skale.dkg.get_channel_started_time(group_index) != 0


def test_complaint_started_time(skale):
    group_index = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    assert skale.dkg.get_complaint_started_time(group_index) == 0


def test_alright_started_time(skale):
    group_index = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    assert skale.dkg.get_alright_started_time(group_index) == 0


def test_complaint_data(skale):
    group_index = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    assert skale.dkg.get_complaint_data(group_index) != [0, 0]


def test_time_of_last_successful_dkg(skale):
    group_index = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    assert skale.dkg.get_time_of_last_successful_dkg(group_index) == 0
