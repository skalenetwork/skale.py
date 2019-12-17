import skale.contracts.data.nodes_data as nodes_data
from skale.dataclasses import CurrentNodeInfo
from skale.schain_config.generator import get_nodes_for_schain
from skale.schain_config.generator import (generate_schain_info, generate_schain_config,
                                           generate_skale_schain_config)
from skale.utils.helper import ip_from_bytes
from tests.constants import (DEFAULT_NODE_NAME, ZERO_ADDRESS, DEFAULT_SCHAIN_NAME, TEST_URL,
                             MIN_NODES_IN_SCHAIN)


TEST_NODE_IP_BYTES = b'\x8aD\xf6V'
TEST_NODE_IP = '10.10.10.10'
NODE_INFO_LEN = 12
SCHAIN_INFO_LEN = 4
TEST_ACCOUNTS_LEN = 2  # because we're creating eveything from one account


TEST_BASE_CONFIG = {
    "params": {},
    "accounts": {}
}


def test_generate_node_info():
    node_info = CurrentNodeInfo(
        node_name=DEFAULT_NODE_NAME,
        node_id=0,
        base_port=10011,
        bind_ip=ip_from_bytes(TEST_NODE_IP_BYTES),
        ima_mainnet=TEST_URL,
        ima_mp_schain=ZERO_ADDRESS,
        ima_mp_mainnet=ZERO_ADDRESS,
        wallets={}
    ).to_config()

    assert isinstance(node_info['bindIP'], str)
    assert isinstance(node_info['nodeID'], int)
    assert isinstance(node_info['nodeName'], str)
    assert isinstance(node_info['basePort'], int)
    assert isinstance(node_info['httpRpcPort'], int)
    assert isinstance(node_info['httpsRpcPort'], int)
    assert isinstance(node_info['wsRpcPort'], int)
    assert isinstance(node_info['wssRpcPort'], int)

    assert isinstance(node_info['imaMainNet'], str)
    assert isinstance(node_info['wallets'], dict)
    assert node_info['imaMessageProxySChain'] == ZERO_ADDRESS
    assert node_info['imaMessageProxyMainNet'] == ZERO_ADDRESS

    assert len(node_info) == NODE_INFO_LEN


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


def test_get_nodes_for_schain(skale):
    schain_nodes = get_nodes_for_schain(skale, DEFAULT_SCHAIN_NAME)
    fields_with_id = nodes_data.FIELDS.copy()
    fields_with_id.append('id')

    assert len(schain_nodes) >= MIN_NODES_IN_SCHAIN
    assert list(schain_nodes[0].keys()) == fields_with_id


def test_generate_skale_schain_config(skale):
    node_index = skale.nodes_data.node_name_to_index(DEFAULT_NODE_NAME)
    config = generate_skale_schain_config(
        skale=skale,
        schain_name=DEFAULT_SCHAIN_NAME,
        node_id=node_index,
        base_config=TEST_BASE_CONFIG,
        ima_mainnet=TEST_URL,
        ima_mp_schain=ZERO_ADDRESS,
        ima_mp_mainnet=ZERO_ADDRESS,
        wallets={}
    )

    assert isinstance(config['params']['chainID'], str)
    assert len(config['accounts'].keys()) == TEST_ACCOUNTS_LEN

    custom_predeployed_address = '0xD2001000000000000000000000000000000000D2'
    assert isinstance(config['accounts'][custom_predeployed_address]['code'], str)
    assert len(config['accounts'][custom_predeployed_address]['storage']) == 2

    assert len(config['skaleConfig']['sChain']['nodes']) == 2
    assert isinstance(config['skaleConfig']['sChain']['schainOwner'], str)
