import pytest


@pytest.mark.parametrize('number_of_nodes', [1])
def test_is_healthy(fair, fair_active_nodes):
    prev_heartbeat_interval = fair.status.contract.functions.heartbeatInterval().call()
    fair.status.set_heartbeat_interval(5 * 60)

    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id

    is_healthy = fair.status.is_healthy(node_id)
    assert isinstance(is_healthy, bool)
    assert is_healthy is False

    main_wallet = fair.wallet
    fair.wallet = fair_active_nodes[0]
    fair.status.alive()
    fair.wallet = main_wallet

    is_healthy_after_alive = fair.status.is_healthy(node_id)
    assert isinstance(is_healthy_after_alive, bool)
    assert is_healthy_after_alive is True

    fair.status.set_heartbeat_interval(prev_heartbeat_interval)


@pytest.mark.parametrize('number_of_nodes', [1])
def test_get_nodes_eligible_for_committee(fair, fair_active_nodes):
    prev_heartbeat_interval = fair.status.contract.functions.heartbeatInterval().call()
    fair.status.set_heartbeat_interval(5 * 60)

    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id

    eligible_nodes = fair.status.get_nodes_eligible_for_committee()
    assert isinstance(eligible_nodes, list)
    assert all(isinstance(node_id, int) for node_id in eligible_nodes)
    assert node_id not in eligible_nodes

    number_of_nodes = len(eligible_nodes)

    fair.status.whitelist_node(node_id)

    eligible_nodes_after_whitelist = fair.status.get_nodes_eligible_for_committee()
    assert node_id not in eligible_nodes_after_whitelist

    main_wallet = fair.wallet
    fair.wallet = fair_active_nodes[0]
    fair.status.alive()
    fair.wallet = main_wallet

    eligible_nodes_after_alive = fair.status.get_nodes_eligible_for_committee()
    assert node_id in eligible_nodes_after_alive
    assert len(eligible_nodes_after_alive) == number_of_nodes + 1

    fair.status.set_heartbeat_interval(prev_heartbeat_interval)


@pytest.mark.parametrize('number_of_nodes', [1])
def test_get_whitelisted_nodes(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id
    fair.status.whitelist_node(node_id)

    whitelisted_nodes = fair.status.get_whitelisted_nodes()
    assert isinstance(whitelisted_nodes, list)
    assert all(isinstance(node_id, int) for node_id in whitelisted_nodes)
    assert node_id in whitelisted_nodes


@pytest.mark.parametrize('number_of_nodes', [1])
def test_is_whitelisted(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id

    is_whitelisted = fair.status.is_whitelisted(node_id)
    assert isinstance(is_whitelisted, bool)
    assert is_whitelisted is False


@pytest.mark.parametrize('number_of_nodes', [1])
def test_alive(fair, fair_active_nodes):
    prev_heartbeat_interval = fair.status.contract.functions.heartbeatInterval().call()
    fair.status.set_heartbeat_interval(5 * 60)

    main_wallet = fair.wallet
    fair.wallet = fair_active_nodes[0]

    fair.status.alive()

    fair.wallet = main_wallet

    fair.status.set_heartbeat_interval(prev_heartbeat_interval)


def test_set_heartbeat_interval(fair):
    prev_heartbeat_interval = fair.status.contract.functions.heartbeatInterval().call()

    interval = 2025
    fair.status.set_heartbeat_interval(interval)

    new_heartbeat_interval = fair.status.contract.functions.heartbeatInterval().call()
    assert new_heartbeat_interval == interval

    fair.status.set_heartbeat_interval(prev_heartbeat_interval)


@pytest.mark.parametrize('number_of_nodes', [1])
def test_whitelist_node(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id

    initial_whitelisted = fair.status.is_whitelisted(node_id)
    assert initial_whitelisted is False

    fair.status.whitelist_node(node_id)
    is_whitelisted_after = fair.status.is_whitelisted(node_id)
    assert isinstance(is_whitelisted_after, bool)
    assert is_whitelisted_after is True


@pytest.mark.parametrize('number_of_nodes', [1])
def test_remove_node_from_whitelist(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id

    fair.status.whitelist_node(node_id)
    assert fair.status.is_whitelisted(node_id) is True

    fair.status.remove_node_from_whitelist(node_id)

    after_removal = fair.status.is_whitelisted(node_id)
    assert after_removal is False
