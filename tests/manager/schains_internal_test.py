""" SKALE chain internal test """

from skale.manager.contracts.schains import FIELDS
from tests.constants import (DEFAULT_NODE_NAME, DEFAULT_SCHAIN_ID,
                             EMPTY_SCHAIN_ARR, DEFAULT_SCHAIN_NAME,
                             MIN_NODES_IN_SCHAIN)


def test_get_raw(skale):
    schain_arr = skale.schains_internal.get_raw(DEFAULT_SCHAIN_ID)
    assert len(FIELDS) == len(schain_arr) + 1  # +1 for chainId


def test_get_raw_not_exist(skale):
    not_exist_schain_id = b'unused_hash'
    schain_arr = skale.schains_internal.get_raw(not_exist_schain_id)
    assert schain_arr == EMPTY_SCHAIN_ARR


def test_get_schains_number(skale):
    assert isinstance(skale.schains_internal.get_schains_number(), int)


def test_get_schain_list_size(skale, empty_account):
    list_size = skale.schains_internal.get_schain_list_size(skale.wallet.address)
    empty_list_size = skale.schains_internal.get_schain_list_size(empty_account.address)

    assert list_size != 0
    assert empty_list_size == 0


def test_get_schain_id_by_index_for_owner(skale):
    schain_id = skale.schains_internal.get_schain_id_by_index_for_owner(
        skale.wallet.address, 0
    )
    schain = skale.schains.get(schain_id)
    assert schain['owner'] == skale.wallet.address


def test_get_node_ids_for_schain(skale):
    schain_node_ids = skale.schains_internal.get_node_ids_for_schain(DEFAULT_SCHAIN_NAME)

    assert isinstance(schain_node_ids, list)
    assert len(schain_node_ids) >= MIN_NODES_IN_SCHAIN


def test_get_schain_ids_for_node(skale):
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    schain_ids_for_node = skale.schains_internal.get_schain_ids_for_node(node_id)

    assert isinstance(schain_ids_for_node, list)
    assert len(schain_ids_for_node) > 0


def test_is_schain_exist(skale):
    assert skale.schains_internal.is_schain_exist(DEFAULT_SCHAIN_NAME)


def test_get_active_schain_ids(skale):
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    active_schains = skale.schains_internal.get_active_schain_ids_for_node(node_id)

    assert isinstance(active_schains, list)
    assert len(active_schains) > 0
