import pytest

from skale.schain_config.generator import (generate_node_info, generate_schain_info,
                                           generate_schain_config, generate_skale_schain_config)
from tests.constants import DEFAULT_NODE_NAME, ZERO_ADDRESS, DEFAULT_SCHAIN_NAME


TEST_NODE_IP_BYTES = b'\x8aD\xf6V'
TEST_NODE_IP = '10.10.10.10'
NODE_INFO_LEN = 8
SCHAIN_INFO_LEN = 4
TEST_ACCOUNTS_LEN = 4

TEST_BASE_CONFIG = {
    "params": {},
    "accounts": {}
}


def test_generate_node_info():
    node_info = generate_node_info(DEFAULT_NODE_NAME, 0, 10011, TEST_NODE_IP_BYTES)

    assert isinstance(node_info['bindIP'], str)
    assert isinstance(node_info['nodeID'], int)
    assert isinstance(node_info['nodeName'], str)
    assert isinstance(node_info['basePort'], int)
    assert isinstance(node_info['httpRpcPort'], int)
    assert isinstance(node_info['httpsRpcPort'], int)
    assert isinstance(node_info['wsRpcPort'], int)
    assert isinstance(node_info['wssRpcPort'], int)
    assert len(node_info) == NODE_INFO_LEN

    with pytest.raises(TypeError):
        generate_node_info(DEFAULT_NODE_NAME, 0, 10011, TEST_NODE_IP)


def test_generate_schain_info():
    schain = {
        'name': DEFAULT_SCHAIN_NAME,
        'owner': ZERO_ADDRESS,
    }
    nodes = []
    schain_info = generate_schain_info(schain, nodes)
    assert isinstance(schain_info['schainID'], int)
    assert isinstance(schain_info['schainName'], str)
    assert isinstance(schain_info['schainOwner'], str)
    assert isinstance(schain_info['nodes'], list)
    assert len(schain_info) == SCHAIN_INFO_LEN


def test_generate_schain_config():
    config = generate_schain_config(TEST_BASE_CONFIG, {}, {})
    assert isinstance(config['accounts'], dict)
    assert isinstance(config['params'], dict)
    assert isinstance(config['skaleConfig']['nodeInfo'], dict)
    assert isinstance(config['skaleConfig']['sChain'], dict)


def test_generate_skale_schain_config(skale):
    node_index = skale.nodes_data.node_name_to_index(DEFAULT_NODE_NAME)
    config = generate_skale_schain_config(skale, DEFAULT_SCHAIN_NAME, node_index, TEST_BASE_CONFIG)

    assert isinstance(config['params']['chainID'], str)
    # 2 because we're creating eveything from one account
    assert len(config['accounts'].keys()) == 2

    custom_predeployed_address = '0xD2001000000000000000000000000000000000D2'
    assert isinstance(config['accounts'][custom_predeployed_address]['code'], str)
    assert len(config['accounts'][custom_predeployed_address]['storage']) == 2

    assert len(config['skaleConfig']['sChain']['nodes']) == 2
    assert isinstance(config['skaleConfig']['sChain']['schainOwner'], str)
