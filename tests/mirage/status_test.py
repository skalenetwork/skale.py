import pytest


@pytest.mark.parametrize('number_of_nodes', [1])
def test_is_healthy(mirage, mirage_active_nodes):
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
