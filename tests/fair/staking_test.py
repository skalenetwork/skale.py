import pytest


@pytest.mark.parametrize('number_of_nodes', [2])
def test_stake_and_retrieve(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id
    
    initial_staked_amount = fair.staking.get_staked_amount()
    initial_staked_nodes = fair.staking.get_staked_nodes()
    initial_node_share = fair.staking.get_node_share(node_id)
    
    assert isinstance(initial_staked_amount, int)
    assert isinstance(initial_staked_nodes, list)
    assert isinstance(initial_node_share, int)
    assert initial_staked_amount == 0
    assert len(initial_staked_nodes) == 0


@pytest.mark.parametrize('number_of_nodes', [2])
def test_stake_to_node(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id
    
    staked_amount = fair.staking.get_staked_amount()
    staked_nodes = fair.staking.get_staked_nodes()
    node_share = fair.staking.get_node_share(node_id)
    
    assert isinstance(staked_amount, int)
    assert isinstance(staked_nodes, list)
    assert isinstance(node_share, int)


@pytest.mark.parametrize('number_of_nodes', [2])
def test_get_staked_amount_for_holder(fair, fair_active_nodes):
    holder_address = fair_active_nodes[0].address
    
    staked_amount = fair.staking.get_staked_amount_for(holder_address)
    staked_nodes = fair.staking.get_staked_nodes_for(holder_address)
    
    assert isinstance(staked_amount, int)
    assert isinstance(staked_nodes, list)
    assert staked_amount >= 0
    assert all(isinstance(node_id, int) for node_id in staked_nodes)


@pytest.mark.parametrize('number_of_nodes', [2])
def test_get_staked_to_node_amount_for(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id
    holder_address = fair_active_nodes[1].address
    
    staked_to_node = fair.staking.get_staked_to_node_amount_for(node_id, holder_address)
    
    assert isinstance(staked_to_node, int)
    assert staked_to_node >= 0


@pytest.mark.parametrize('number_of_nodes', [1])
def test_fee_related_functions(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id
    
    earned_fee = fair.staking.get_earned_fee_amount(node_id)
    
    assert isinstance(earned_fee, int)
    assert earned_fee >= 0


@pytest.mark.parametrize('number_of_nodes', [1])
def test_node_share_calculation(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id
    
    node_share = fair.staking.get_node_share(node_id)
    
    assert isinstance(node_share, int)
    assert node_share >= 0


def test_staking_view_functions_with_no_nodes(fair):
    staked_amount = fair.staking.get_staked_amount()
    staked_nodes = fair.staking.get_staked_nodes()
    
    assert isinstance(staked_amount, int)
    assert isinstance(staked_nodes, list)
    assert staked_amount == 0
    assert len(staked_nodes) == 0


@pytest.mark.parametrize('number_of_nodes', [2])
def test_get_staked_to_node_amount(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id
    
    staked_to_node = fair.staking.get_staked_to_node_amount(node_id)
    
    assert isinstance(staked_to_node, int)
    assert staked_to_node >= 0
