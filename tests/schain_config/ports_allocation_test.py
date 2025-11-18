import pytest

from skale.schain_config import PORTS_PER_SCHAIN
from skale.schain_config.ports_allocation import (
    calc_schain_base_port,
    get_schain_base_port_on_node,
    get_schain_index_in_node,
)
from skale.utils.exceptions import SChainNotFoundException
from skale.utils.helper import schain_name_to_hash
from tests.constants import DEFAULT_NODE_NAME, DEFAULT_NODE_PORT, DEFAULT_SCHAIN_INDEX


def test_get_schain_base_port_on_node(skale, schain):
    schain_hash = schain_name_to_hash(schain)
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    schain_hashes = skale.schains_internal.get_schain_hashes_for_node(node_id)
    schain_port_on_node = get_schain_base_port_on_node(
        schain_hashes, schain_hash, DEFAULT_NODE_PORT
    )
    assert schain_port_on_node == DEFAULT_NODE_PORT


def test_get_schain_index_in_node(skale, schain):
    schain_hash = schain_name_to_hash(schain)
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    schain_hashes = skale.schains_internal.get_schain_hashes_for_node(node_id)
    index = get_schain_index_in_node(schain_hash, schain_hashes)
    assert isinstance(index, int)

    wrong_schain_hash = schain_name_to_hash('ABCabcd')
    with pytest.raises(SChainNotFoundException):
        get_schain_index_in_node(wrong_schain_hash, schain_hashes)


def test_calc_schain_base_port():
    schain_base_port = calc_schain_base_port(DEFAULT_NODE_PORT, DEFAULT_SCHAIN_INDEX)
    schain_base_port_next = calc_schain_base_port(DEFAULT_NODE_PORT, DEFAULT_SCHAIN_INDEX + 1)
    schain_base_port_calc = schain_base_port + ((DEFAULT_SCHAIN_INDEX + 1) * PORTS_PER_SCHAIN)

    assert schain_base_port == DEFAULT_NODE_PORT
    assert schain_base_port_calc == schain_base_port_next
