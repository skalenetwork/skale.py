from skale.utils.contracts_provision.main import generate_random_node_data


def test_dry_run(skale):
    active_node_ids_before = skale.nodes_data.get_active_node_ids()

    ip, _, port, name = generate_random_node_data()
    tx_res = skale.manager.create_node(ip, port, name, dry_run=True)

    assert tx_res.hash is None
    assert tx_res.data == []

    active_node_ids_after = skale.nodes_data.get_active_node_ids()
    assert len(active_node_ids_after) == len(active_node_ids_before)

    tx_res = skale.manager.create_node(ip, port, name, dry_run=False, wait_for=True)

    assert tx_res.hash is not None

    active_node_ids_after_transaction = skale.nodes_data.get_active_node_ids()
    assert len(active_node_ids_after_transaction) == len(active_node_ids_before) + 1
