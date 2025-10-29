import socket
from unittest.mock import Mock

from skale.fair_config.committee_nodes import get_nodes_from_two_operational_committees
from skale.types.committee import Committee, CommitteeIndex, Timestamp
from skale.types.dkg import DkgId, Fp2Point, G2Point
from skale.types.node import FairNode, NodeId


def create_mock_committee(node_ids, dkg_id=1, starting_timestamp=1000):
    return Committee(
        node_ids=node_ids,
        dkg_id=DkgId(dkg_id),
        common_public_key=G2Point(x=Fp2Point(0, 0), y=Fp2Point(0, 0)),
        starting_timestamp=Timestamp(starting_timestamp),
    )


def create_mock_node(node_id, address='0x123', name=None):
    if name is None:
        name = f'node-{node_id}'

    mock_node = Mock(spec=FairNode)
    mock_node.id = NodeId(node_id)
    mock_node.ip = socket.inet_aton(f'127.0.0.{node_id}')
    mock_node.ip_str = f'127.0.0.{node_id}'
    mock_node.domain_name = f'domain-{node_id}'
    mock_node.address = address
    mock_node.port = 10000
    mock_node.name = name
    mock_node.to_dict.return_value = {
        'id': node_id,
        'ip_str': f'127.0.0.{node_id}',
        'domain_name': f'domain-{node_id}',
        'address': address,
        'port': 10000,
        'name': name,
    }
    return mock_node


def test_get_nodes_from_last_two_committees_first_committee():
    fair = Mock()
    fair.committee.last_committee_index.return_value = 0

    node_ids = [NodeId(1), NodeId(2)]
    committee_0 = create_mock_committee(node_ids, starting_timestamp=1500)

    def get_committee_side_effect(index):
        return committee_0

    fair.committee.get_committee.side_effect = get_committee_side_effect
    fair.web3.to_checksum_address.return_value = '0x0000000000000000000000000000000000000000'

    nodes = {}
    for node_id in node_ids:
        node = create_mock_node(node_id, f'0xaddress{node_id}')
        nodes[node_id] = node
    fair.nodes.get.side_effect = lambda nid: nodes[nid]
    fair.staking.get_reward_wallet.side_effect = lambda node_id: f'0xreward{node_id}'
    fair.node.get_public_key.side_effect = lambda node_id: f'0xpublickey{node_id}'

    result = get_nodes_from_two_operational_committees(fair)

    assert len(result) == 2
    assert result[0]['index'] == 0
    assert result[0]['ts'] == 0
    assert result[1]['index'] == 0
    assert result[1]['ts'] == 1500
    assert result[0]['staking_contract_address'] == '0x0000000000000000000000000000000000000000'
    assert result[1]['staking_contract_address'] == '0x0000000000000000000000000000000000000000'


def test_get_nodes_from_last_two_committees_multiple_committees():
    fair = Mock()
    fair.committee.last_committee_index.return_value = 2
    fair.nodes.active_node_exists.return_value = True
    fair.web3.eth.get_block = Mock(return_value={'timestamp': 1018})

    node_ids_1 = [NodeId(1)]
    node_ids_2 = [NodeId(2)]
    committee_0 = create_mock_committee(node_ids_1 + node_ids_2, starting_timestamp=0)
    committee_1 = create_mock_committee(node_ids_1, starting_timestamp=1000)
    committee_2 = create_mock_committee(node_ids_2, starting_timestamp=2000)

    def get_committee_side_effect(index):
        if index == CommitteeIndex(0):
            return committee_0
        elif index == CommitteeIndex(1):
            return committee_1
        elif index == CommitteeIndex(2):
            return committee_2

    fair.committee.get_committee.side_effect = get_committee_side_effect
    fair.web3.to_checksum_address.return_value = '0x0000000000000000000000000000000000000000'
    fair.staking.contract.address = '0x7777777777777777777777777777777777777777'

    nodes = {}
    for node_id in node_ids_1 + node_ids_2:
        nodes[node_id] = create_mock_node(node_id)
    fair.nodes.get.side_effect = lambda nid: nodes[nid]
    fair.staking.get_reward_wallet.return_value = '0xreward'
    fair.node.get_public_key.side_effect = lambda node_id: f'0xpublickey{node_id}'

    result = get_nodes_from_two_operational_committees(fair)

    assert len(result) == 2
    assert result[0]['index'] == 1
    assert result[0]['ts'] == 1000
    assert result[1]['index'] == 2
    assert result[1]['ts'] == 2000
    assert result[0]['staking_contract_address'] == '0x7777777777777777777777777777777777777777'
    assert result[1]['staking_contract_address'] == '0x7777777777777777777777777777777777777777'


def test_get_nodes_from_last_two_committees_structure():
    fair = Mock()
    fair.committee.last_committee_index.return_value = 0

    node_ids = [NodeId(1)]
    committee = create_mock_committee(node_ids)

    def get_committee_side_effect(index):
        return committee

    fair.committee.get_committee.side_effect = get_committee_side_effect
    fair.web3.to_checksum_address.return_value = '0x0000000000000000000000000000000000000000'
    fair.nodes.get.return_value = create_mock_node(1)
    fair.staking.get_reward_wallet.return_value = '0xreward'
    fair.node.get_public_key.side_effect = lambda node_id: f'0xpublickey{node_id}'

    result = get_nodes_from_two_operational_committees(fair)

    for group in result:
        assert 'index' in group
        assert 'ts' in group
        assert 'group' in group
        assert 'committee' in group
        assert isinstance(group['index'], int)
        assert isinstance(group['ts'], int)
        assert isinstance(group['group'], list)
        assert isinstance(group['committee'], Committee)
