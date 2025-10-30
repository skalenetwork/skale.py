"""SKALE manager test"""

import random
from unittest import mock
from unittest.mock import Mock

import pytest
import web3
from hexbytes import HexBytes

from skale.transactions.result import DryRunRevertError, TransactionFailedError
from skale.utils.contracts_provision import DEFAULT_DOMAIN_NAME
from skale.utils.contracts_provision.main import (
    generate_random_node_data,
    generate_random_schain_data,
)
from skale.wallets.web3_wallet import generate_wallet
from tests.constants import TEST_GAS_LIMIT


def test_get_bounty(skale):
    node_id = 0
    nonce = skale.web3.eth.get_transaction_count(skale.wallet.address)
    contract_address = skale.manager.address
    chain_id = skale.web3.eth.chain_id
    expected_txn = {
        'value': 0,
        'gasPrice': skale.gas_price,
        'chainId': chain_id,
        'gas': TEST_GAS_LIMIT,
        'nonce': nonce,
        'type': 1,
        'to': contract_address,
        'data': ('0xee8c4bbf0000000000000000000000000000000000000000000000000000000000000000'),
    }
    exp = skale.web3.eth.account.sign_transaction(
        expected_txn, skale.wallet._private_key
    ).raw_transaction
    with mock.patch.object(
        skale.manager.contract.functions.getBounty, 'call', new=Mock(return_value=[])
    ):
        with mock.patch.object(web3.eth.Eth, 'send_raw_transaction') as send_tx_mock:
            send_tx_mock.return_value = b'hexstring'
            skale.manager.get_bounty(node_id, wait_for=False, gas_limit=TEST_GAS_LIMIT)
            send_tx_mock.assert_called_with(HexBytes(exp))


def test_create_delete_schain(skale, nodes):
    schains_ids = skale.schains_internal.get_all_schains_ids()

    type_of_nodes, lifetime_seconds, name = generate_random_schain_data(skale)
    price_in_wei = skale.schains.get_schain_price(type_of_nodes, lifetime_seconds)

    try:
        tx_res = skale.manager.create_schain(
            lifetime_seconds, type_of_nodes, price_in_wei, name, wait_for=True
        )

        assert tx_res.receipt['status'] == 1

        schains_ids_number_after = skale.schains_internal.get_schains_number()
        assert schains_ids_number_after == len(schains_ids) + 1
        schains_ids_after = skale.schains_internal.get_all_schains_ids()

        schains_names = [skale.schains.get(sid).name for sid in schains_ids_after]
        assert name in schains_names
    finally:
        skale.manager.delete_schain(name, wait_for=True)

    schains_ids_number_after = skale.schains_internal.get_schains_number()
    assert schains_ids_number_after == len(schains_ids)
    schains_ids_after = skale.schains_internal.get_all_schains_ids()

    schains_names = [skale.schains.get(sid).name for sid in schains_ids_after]
    assert name not in schains_names


def test_delete_schain_by_root(skale, nodes):
    schains_ids = skale.schains_internal.get_all_schains_ids()
    name = ''.join(random.choice('abcde') for _ in range(4))
    try:
        skale.manager.create_default_schain(name)
    finally:
        skale.manager.delete_schain_by_root(name, wait_for=True)

    schains_ids_number_after = skale.schains_internal.get_schains_number()
    assert schains_ids_number_after == len(schains_ids)
    schains_ids_after = skale.schains_internal.get_all_schains_ids()

    schains_names = [skale.schains.get(sid).name for sid in schains_ids_after]
    assert name not in schains_names


def test_create_delete_default_schain(skale, nodes):
    schains_ids = skale.schains_internal.get_all_schains_ids()
    _, _, name = generate_random_schain_data(skale)
    try:
        skale.manager.create_default_schain(name)

        schains_ids_number_after = skale.schains_internal.get_schains_number()
        assert schains_ids_number_after == len(schains_ids) + 1
        schains_ids_after = skale.schains_internal.get_all_schains_ids()

        schains_names = [skale.schains.get(sid).name for sid in schains_ids_after]
        assert name in schains_names
    finally:
        skale.manager.delete_schain(name)

    schains_ids_number_after = skale.schains_internal.get_schains_number()
    assert schains_ids_number_after == len(schains_ids)
    schains_ids_after = skale.schains_internal.get_all_schains_ids()

    schains_names = [skale.schains.get(sid).name for sid in schains_ids_after]
    assert name not in schains_names


def test_create_node_status_0(failed_skale):
    skale = failed_skale
    ip, public_ip, port, name = generate_random_node_data()
    tx_res = skale.manager.create_node(
        ip,
        port,
        name,
        domain_name=DEFAULT_DOMAIN_NAME,
        wait_for=True,
        skip_dry_run=True,
        raise_for_status=False,
    )
    assert tx_res.receipt['status'] == 0
    with pytest.raises(TransactionFailedError):
        tx_res.raise_for_status()


def test_node_exit_with_no_schains(skale, nodes):
    node_id, *_ = nodes
    skale.nodes.init_exit(node_id, wait_for=True)
    tx_res = skale.manager.node_exit(node_id, wait_for=True)
    assert tx_res.receipt['status'] == 1
    assert skale.nodes.get_node_status(node_id) == 2


def test_failed_node_exit(skale, block_in_seconds):
    # block_in_seconds fixture to return transaction revert in a same way as geth does
    not_existed_node_id = 1
    with pytest.raises(DryRunRevertError):
        skale.manager.node_exit(not_existed_node_id, wait_for=True, gas_limit=TEST_GAS_LIMIT)


def test_grant_role(skale):
    wallet = generate_wallet(skale.web3)
    default_admin_role = skale.manager.default_admin_role()
    assert not skale.manager.has_role(default_admin_role, wallet.address)

    skale.manager.grant_role(default_admin_role, wallet.address, wait_for=True)
    assert skale.manager.has_role(default_admin_role, wallet.address)


def test_grant_admin_role(skale):
    wallet = generate_wallet(skale.web3)
    admin_role = skale.manager.admin_role()
    assert not skale.manager.has_role(admin_role, wallet.address)

    skale.manager.grant_role(admin_role, wallet.address, wait_for=True)
    assert skale.manager.has_role(admin_role, wallet.address)
