import skale.contracts.manager.nodes as nodes
from skale.schain_config.generator import get_nodes_for_schain, get_schain_nodes_with_schains
from tests.constants import MIN_NODES_IN_SCHAIN


def test_get_nodes_for_schain(skale, schain):
    schain_name = schain
    schain_nodes = get_nodes_for_schain(skale, schain_name)
    fields_with_id = nodes.FIELDS.copy()
    fields_with_id.append('id')

    assert len(schain_nodes) >= MIN_NODES_IN_SCHAIN
    assert set(schain_nodes[0].keys()) == set(fields_with_id)


def test_get_schain_nodes_with_schains(skale, schain):
    schain_name = schain
    nodes_with_schains = get_schain_nodes_with_schains(skale, schain_name)
    assert isinstance(nodes_with_schains[0]['schains'], list)
    assert nodes_with_schains[0]['schains'][0].mainnet_owner == skale.wallet.address
