""" SKALE monitors data test """

from tests.constants import DEFAULT_NODE_NAME, DEFAULT_NODE_INDEX


def test_get_checked_array_raw(skale):
    node_id = skale.nodes_data.node_name_to_index(DEFAULT_NODE_NAME)
    raw_checked_array = skale.monitors_data._MonitorsData__get_checked_array_raw(node_id)
    assert isinstance(raw_checked_array[0], bytes)


def test_get_checked_array(skale):
    node_id = skale.nodes_data.node_name_to_index(DEFAULT_NODE_NAME)
    checked_array = skale.monitors_data.get_checked_array(node_id)

    assert 'id' in checked_array[0]
    assert 'ip' in checked_array[0]
    assert 'rep_date' in checked_array[0]


def test_get_last_bounty_block(skale):
    last_bounty_block = skale.monitors_data.get_last_bounty_block(DEFAULT_NODE_INDEX)
    assert isinstance(last_bounty_block, int)


def test_get_last_received_verdict_block(skale):
    last_verdict_block = skale.monitors_data.get_last_received_verdict_block(DEFAULT_NODE_INDEX)
    assert isinstance(last_verdict_block, int)
