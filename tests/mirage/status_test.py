import pytest


@pytest.mark.parametrize('number_of_nodes', [1])
def test_is_healthy(mirage, mirage_active_nodes):
    prev_heartbeat_interval = mirage.status.contract.functions.heartbeatInterval().call()
    mirage.status.set_heartbeat_interval(5 * 60)

    node = mirage.nodes.get_by_address(mirage_active_nodes[0].address)
    node_id = node.id

    is_healthy = mirage.status.is_healthy(node_id)
    assert isinstance(is_healthy, bool)
    assert is_healthy is False

    main_wallet = mirage.wallet
    mirage.wallet = mirage_active_nodes[0]
    mirage.status.alive()
    mirage.wallet = main_wallet

    is_healthy_after_alive = mirage.status.is_healthy(node_id)
    assert isinstance(is_healthy_after_alive, bool)
    assert is_healthy_after_alive is True

    mirage.status.set_heartbeat_interval(prev_heartbeat_interval)


@pytest.mark.parametrize('number_of_nodes', [1])
def test_get_nodes_eligible_for_committee(mirage, mirage_active_nodes):
    prev_heartbeat_interval = mirage.status.contract.functions.heartbeatInterval().call()
    mirage.status.set_heartbeat_interval(5 * 60)

    node = mirage.nodes.get_by_address(mirage_active_nodes[0].address)
    node_id = node.id

    eligible_nodes = mirage.status.get_nodes_eligible_for_committee()
    assert isinstance(eligible_nodes, list)
    assert all(isinstance(node_id, int) for node_id in eligible_nodes)
    assert node_id not in eligible_nodes

    number_of_nodes = len(eligible_nodes)

    mirage.status.whitelist_node(node_id)

    eligible_nodes_after_whitelist = mirage.status.get_nodes_eligible_for_committee()
    assert node_id not in eligible_nodes_after_whitelist

    main_wallet = mirage.wallet
    mirage.wallet = mirage_active_nodes[0]
    mirage.status.alive()
    mirage.wallet = main_wallet

    eligible_nodes_after_alive = mirage.status.get_nodes_eligible_for_committee()
    assert node_id in eligible_nodes_after_alive
    assert len(eligible_nodes_after_alive) == number_of_nodes + 1

    mirage.status.set_heartbeat_interval(prev_heartbeat_interval)


@pytest.mark.parametrize('number_of_nodes', [1])
def test_get_whitelisted_nodes(mirage, mirage_active_nodes):
    node = mirage.nodes.get_by_address(mirage_active_nodes[0].address)
    node_id = node.id
    mirage.status.whitelist_node(node_id)

    whitelisted_nodes = mirage.status.get_whitelisted_nodes()
    assert isinstance(whitelisted_nodes, list)
    assert all(isinstance(node_id, int) for node_id in whitelisted_nodes)
    assert node_id in whitelisted_nodes


@pytest.mark.parametrize('number_of_nodes', [1])
def test_is_whitelisted(mirage, mirage_active_nodes):
    node = mirage.nodes.get_by_address(mirage_active_nodes[0].address)
    node_id = node.id

    is_whitelisted = mirage.status.is_whitelisted(node_id)
    assert isinstance(is_whitelisted, bool)
    assert is_whitelisted is False


@pytest.mark.parametrize('number_of_nodes', [1])
def test_alive(mirage, mirage_active_nodes):
    prev_heartbeat_interval = mirage.status.contract.functions.heartbeatInterval().call()
    mirage.status.set_heartbeat_interval(5 * 60)

    main_wallet = mirage.wallet
    mirage.wallet = mirage_active_nodes[0]

    mirage.status.alive()

    mirage.wallet = main_wallet

    mirage.status.set_heartbeat_interval(prev_heartbeat_interval)


def test_set_heartbeat_interval(mirage):
    prev_heartbeat_interval = mirage.status.contract.functions.heartbeatInterval().call()

    interval = 2025
    mirage.status.set_heartbeat_interval(interval)

    new_heartbeat_interval = mirage.status.contract.functions.heartbeatInterval().call()
    assert new_heartbeat_interval == interval

    mirage.status.set_heartbeat_interval(prev_heartbeat_interval)


@pytest.mark.parametrize('number_of_nodes', [1])
def test_whitelist_node(mirage, mirage_active_nodes):
    node = mirage.nodes.get_by_address(mirage_active_nodes[0].address)
    node_id = node.id

    initial_whitelisted = mirage.status.is_whitelisted(node_id)
    assert initial_whitelisted is False

    mirage.status.whitelist_node(node_id)
    is_whitelisted_after = mirage.status.is_whitelisted(node_id)
    assert isinstance(is_whitelisted_after, bool)
    assert is_whitelisted_after is True


@pytest.mark.parametrize('number_of_nodes', [1])
def test_remove_node_from_whitelist(mirage, mirage_active_nodes):
    node = mirage.nodes.get_by_address(mirage_active_nodes[0].address)
    node_id = node.id

    mirage.status.whitelist_node(node_id)
    assert mirage.status.is_whitelisted(node_id) is True

    mirage.status.remove_node_from_whitelist(node_id)

    after_removal = mirage.status.is_whitelisted(node_id)
    assert after_removal is False
