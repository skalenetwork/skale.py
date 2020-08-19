import skale.contracts.manager.nodes as nodes
from skale.schain_config.generator import get_nodes_for_schain, get_schain_nodes_with_schains
from tests.constants import (DEFAULT_SCHAIN_NAME, MIN_NODES_IN_SCHAIN)


def test_get_nodes_for_schain(skale):
    schain_nodes = get_nodes_for_schain(skale, DEFAULT_SCHAIN_NAME)
    fields_with_id = nodes.FIELDS.copy()
    fields_with_id.append('id')

    assert len(schain_nodes) >= MIN_NODES_IN_SCHAIN
    assert list(schain_nodes[0].keys()) == fields_with_id


def test_get_schain_nodes_with_schains(skale):
    nodes_with_schains = get_schain_nodes_with_schains(skale, DEFAULT_SCHAIN_NAME)
    assert isinstance(nodes_with_schains[0]['schains'], list)
    assert isinstance(nodes_with_schains[0]['schains'][0]['owner'], str)
    assert isinstance(nodes_with_schains[0]['bls_public_key'], tuple)
