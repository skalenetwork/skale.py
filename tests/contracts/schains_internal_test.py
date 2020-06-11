""" SKALE chain internal test """

import mock

from skale.contracts.schains import FIELDS
from tests.constants import (DEFAULT_NODE_NAME, DEFAULT_SCHAIN_ID,
                             EMPTY_SCHAIN_ARR, DEFAULT_SCHAIN_NAME,
                             MIN_NODES_IN_SCHAIN, DEFAULT_SCHAIN_INDEX)


def test_get_raw(skale):
    schain_arr = skale.schains_internal.get_raw(DEFAULT_SCHAIN_ID)
    assert len(FIELDS) == len(schain_arr)+1  # +1 for chainId


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


def test_get_previous_groups_public_key(skale):
    group_id = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    public_key = skale.schains_internal.get_previous_groups_public_key(group_id)
    assert len(public_key) == 4


def test_get_rotation(skale):
    assert skale.schains_internal.get_rotation(DEFAULT_SCHAIN_NAME) == {
        'leaving_node': 0,
        'new_node': 0,
        'finish_ts': 0,
        'rotation_id': 0
    }


def test_is_group_failed_dkg(skale):
    assert skale.schains_internal.is_group_failed_dkg(DEFAULT_SCHAIN_ID)


def test_is_schain_exist(skale):
    assert skale.schains_internal.is_schain_exist(DEFAULT_SCHAIN_NAME)


def test_get_group_public_key(skale):
    assert skale.schains_internal.get_groups_public_key(
        DEFAULT_SCHAIN_ID) == [0, 0, 0, 0]


def test_get_leaving_history(skale):
    empty = skale.schains_internal.get_leaving_history(DEFAULT_SCHAIN_INDEX)
    assert empty == []
    with mock.patch.object(skale.schains_internal.contract.functions.getLeavingHistory, 'call') \
            as call_mock:
        call_mock.return_value = [(DEFAULT_SCHAIN_ID, 1000), (DEFAULT_SCHAIN_ID, 2000)]
        history = skale.schains_internal.get_leaving_history(DEFAULT_SCHAIN_INDEX)
        assert isinstance(history, list)
        assert history == [
            {
                'id': DEFAULT_SCHAIN_ID,
                'finished_rotation': 1000
            },
            {
                'id': DEFAULT_SCHAIN_ID,
                'finished_rotation': 2000
            }
        ]
