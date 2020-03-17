import pytest

from skale.schain_config.ports_allocation import (get_schain_base_port_on_node,
                                                  calc_schain_base_port, get_schain_index_in_node)
from skale.utils.exceptions import SChainNotFoundException
from skale.schain_config import PORTS_PER_SCHAIN
from tests.constants import (DEFAULT_NODE_NAME, DEFAULT_SCHAIN_NAME, DEFAULT_NODE_PORT,
                             DEFAULT_SCHAIN_INDEX)


def test_get_schain_base_port_on_node(skale):
    node_id = skale.nodes_data.node_name_to_index(DEFAULT_NODE_NAME)
    schains_on_node = skale.schains_data.get_schains_for_node(node_id)
    schain_port_on_node = get_schain_base_port_on_node(
        schains_on_node,
        DEFAULT_SCHAIN_NAME,
        DEFAULT_NODE_PORT
    )
    assert schain_port_on_node == DEFAULT_NODE_PORT


def test_get_schain_index_in_node(skale):
    node_id = skale.nodes_data.node_name_to_index(DEFAULT_NODE_NAME)
    schains_on_node = skale.schains_data.get_schains_for_node(node_id)
    index = get_schain_index_in_node(DEFAULT_SCHAIN_NAME, schains_on_node)
    assert isinstance(index, int)
    with pytest.raises(SChainNotFoundException):
        get_schain_index_in_node('ABCabc', schains_on_node)


def test_calc_schain_base_port():
    schain_base_port = calc_schain_base_port(DEFAULT_NODE_PORT, DEFAULT_SCHAIN_INDEX)
    schain_base_port_next = calc_schain_base_port(DEFAULT_NODE_PORT, DEFAULT_SCHAIN_INDEX + 1)
    schain_base_port_calc = schain_base_port + ((DEFAULT_SCHAIN_INDEX + 1) * PORTS_PER_SCHAIN)

    assert schain_base_port == DEFAULT_NODE_PORT
    assert schain_base_port_calc == schain_base_port_next
