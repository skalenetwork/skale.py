import pytest

from web3.exceptions import ContractLogicError

from skale.utils.contracts_provision.utils import generate_random_node_data


@pytest.fixture
@pytest.mark.parametrize('number_of_nodes', [1])
def mirage_node(mirage, node_wallets):
    main_wallet = mirage.wallet
    mirage.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()
    mirage.nodes.register(ip=ip, port=port)
    mirage.wallet = main_wallet
    try:
        yield node_wallets[0]
    finally:
        """TODO: Remove the node from the mirage instance."""


def test_get(mirage):
    node = mirage.nodes.get(1)
    assert node is not None
    print(node)
    assert node.id == 1
    assert 1


@pytest.mark.parametrize('number_of_nodes', [1])
def test_register(mirage, node_wallets):
    main_wallet = mirage.wallet
    mirage.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()

    with pytest.raises(ContractLogicError):
        mirage.nodes.get_by_address(mirage.wallet.address)

    active_node_ids_before = mirage.nodes.get_active_node_ids()
    mirage.nodes.register(ip=ip, port=port)
    active_node_ids_after = mirage.nodes.get_active_node_ids()

    assert len(active_node_ids_after) == len(active_node_ids_before) + 1

    node = mirage.nodes.get_by_address(mirage.wallet.address)
    assert node.address == mirage.wallet.address

    mirage.wallet = main_wallet
