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
    assert initial_staked_amount >= 0
    if initial_staked_amount == 0:
        assert len(initial_staked_nodes) == 0
    else:
        assert len(initial_staked_nodes) > 0


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
    assert staked_amount >= 0
    if staked_amount == 0:
        assert len(staked_nodes) == 0
    else:
        assert len(staked_nodes) > 0


@pytest.mark.parametrize('number_of_nodes', [2])
def test_get_staked_to_node_amount(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id

    staked_to_node = fair.staking.get_staked_to_node_amount(node_id)

    assert isinstance(staked_to_node, int)
    assert staked_to_node >= 0


@pytest.mark.parametrize('number_of_nodes', [1])
def test_get_node_fee_rate(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id

    fee_rate = fair.staking.get_node_fee_rate(node_id)

    assert isinstance(fee_rate, int)
    assert fee_rate >= 0


def test_staking_public_methods_present(fair):
    staking = fair.staking
    public_attrs = [
        'add_allowed_receiver',
        'remove_allowed_receiver',
        'request_send_all_fees',
        'request_all_fees',
        'set_fee_rate',
        'request_fees',
        'request_send_fees',
        'get_earned_fee_amount',
        'request_retrieve',
        'request_retrieve_all',
        'claim_request',
        'set_self_stake_requirement',
        'set_retrieving_delay',
        'get_total_in_exit_queue',
        'get_retrieving_delay',
        'get_exit_requests_count_for',
        'get_my_exit_requests_count',
        'get_exit_request',
        'get_exit_request_at',
        'get_exit_requests_for',
        'get_unlocked_exit_request_for',
        'is_request_unlocked',
        'stake',
    ]
    for attr in public_attrs:
        assert hasattr(staking, attr)


@pytest.mark.parametrize('number_of_nodes', [1])
def test_self_stake_requirement_update(fair, fair_active_nodes):
    staking = fair.staking
    original = staking.self_stake_requirement()
    assert isinstance(original, int)
    new_value = original + 1 if original > 0 else 2
    staking.set_self_stake_requirement(new_value)
    updated = staking.self_stake_requirement()
    assert updated == new_value


@pytest.mark.parametrize('number_of_nodes', [1])
def test_exit_queue_getters_initial(fair, fair_active_nodes):
    staking = fair.staking
    node_id = fair.nodes.get_by_address(fair_active_nodes[0].address).id
    assert isinstance(staking.get_retrieving_delay(), int)
    total_exit_queue = staking.get_total_in_exit_queue(staking.skale.wallet.address)
    assert isinstance(total_exit_queue, int)
    assert isinstance(staking.is_within_stake_limit(node_id), bool)
    assert staking.get_my_exit_requests_count() >= 0
    assert total_exit_queue >= 0
