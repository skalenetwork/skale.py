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
def test_register_active_node(mirage, node_wallets):
    main_wallet = mirage.wallet
    mirage.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()

    with pytest.raises(ContractLogicError):
        mirage.nodes.get_by_address(mirage.wallet.address)

    active_node_ids_before = mirage.nodes.get_active_node_ids()
    mirage.nodes.register_active(ip=ip, port=port)
    active_node_ids_after = mirage.nodes.get_active_node_ids()

    assert len(active_node_ids_after) == len(active_node_ids_before) + 1

    node = mirage.nodes.get_by_address(mirage.wallet.address)
    assert node.address == mirage.wallet.address

    mirage.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [1])
def test_register_passive_node(mirage, node_wallets):
    main_wallet = mirage.wallet
    mirage.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()

    with pytest.raises(ContractLogicError):
        mirage.nodes.get_passive_node_ids_for_address(mirage.wallet.address)

    passive_node_ids_before = mirage.nodes.get_passive_node_ids()
    mirage.nodes.register_passive(ip=ip, port=port)
    passive_node_ids_after = mirage.nodes.get_passive_node_ids()

    assert len(passive_node_ids_after) == len(passive_node_ids_before) + 1

    node_id = mirage.nodes.get_passive_node_ids_for_address(mirage.wallet.address)[0]
    assert node_id in passive_node_ids_after

    mirage.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [1])
def test_set_domain_name(mirage, node_wallets):
    main_wallet = mirage.wallet
    mirage.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()

    mirage.nodes.register_active(ip=ip, port=port)
    node = mirage.nodes.get_by_address(mirage.wallet.address)
    node_id = node.id

    domain_name = 'test-domain.example.com'
    mirage.nodes.set_domain_name(node_id, domain_name)

    updated_node = mirage.nodes.get(node_id)
    assert updated_node.domain_name == domain_name

    mirage.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [1])
def test_set_ip_address(mirage, node_wallets):
    main_wallet = mirage.wallet
    mirage.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()

    mirage.nodes.register_active(ip=ip, port=port)
    node = mirage.nodes.get_by_address(mirage.wallet.address)
    node_id = node.id

    new_ip, _, new_port, _ = generate_random_node_data()
    mirage.nodes.set_ip_address(node_id, new_ip, new_port)

    updated_node = mirage.nodes.get(node_id)
    assert updated_node.ip_str == new_ip
    assert updated_node.port == new_port

    mirage.wallet = main_wallet


def test_set_committee(mirage, node_wallets):
    original_committee_address = mirage.committee.address
    committee_address = node_wallets[0].address
    mirage.nodes.set_committee(committee_address)

    # Try to register new active node, should fail because of wrong committee address
    main_wallet = mirage.wallet
    mirage.wallet = node_wallets[1]
    ip, _, port, _ = generate_random_node_data()

    with pytest.raises(ContractLogicError):
        mirage.nodes.register_active(ip=ip, port=port)

    # Restore original wallet and committee address
    mirage.wallet = main_wallet
    mirage.nodes.set_committee(original_committee_address)


def test_request_change_owner(mirage, node_wallets):
    main_wallet = mirage.wallet
    mirage.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()

    mirage.nodes.register_passive(ip=ip, port=port)
    node_id = mirage.nodes.get_passive_node_ids_for_address(mirage.wallet.address)[0]

    new_owner = node_wallets[1].address
    mirage.nodes.request_change_owner(node_id, new_owner)

    mirage.wallet = main_wallet


def test_confirm_owner_change(mirage, node_wallets):
    main_wallet = mirage.wallet
    mirage.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()

    mirage.nodes.register_passive(ip=ip, port=port)
    node_id = mirage.nodes.get_passive_node_ids_for_address(mirage.wallet.address)[0]

    new_owner = node_wallets[1].address
    mirage.nodes.request_change_owner(node_id, new_owner)

    mirage.wallet = node_wallets[1]
    mirage.nodes.confirm_owner_change(node_id)

    mirage.wallet = main_wallet


def test_get_id(mirage, node_wallets):
    main_wallet = mirage.wallet
    mirage.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()

    mirage.nodes.register_active(ip=ip, port=port)
    node_id = mirage.nodes.get_id(mirage.wallet.address)
    assert node_id > 0

    mirage.wallet = main_wallet


def test_get_passive_node_ids_for_address(mirage, node_wallets):
    main_wallet = mirage.wallet
    mirage.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()

    mirage.nodes.register_passive(ip=ip, port=port)

    node_ids = mirage.nodes.get_passive_node_ids_for_address(mirage.wallet.address)
    assert len(node_ids) == 1
    assert node_ids[0] > 0

    new_ip, _, new_port, _ = generate_random_node_data()
    mirage.nodes.register_passive(ip=new_ip, port=new_port)

    node_ids = mirage.nodes.get_passive_node_ids_for_address(mirage.wallet.address)
    assert len(node_ids) == 2
    assert node_ids[0] > 0
    assert node_ids[1] > 0

    mirage.wallet = main_wallet


def test_get_passive_node_ids(mirage, node_wallets):
    main_wallet = mirage.wallet
    mirage.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()

    passive_node_ids_before = mirage.nodes.get_passive_node_ids()
    mirage.nodes.register_passive(ip=ip, port=port)
    passive_node_ids_after = mirage.nodes.get_passive_node_ids()

    assert len(passive_node_ids_after) == len(passive_node_ids_before) + 1

    mirage.wallet = main_wallet


def test_get_active_node_ids(mirage, node_wallets):
    main_wallet = mirage.wallet
    mirage.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()

    active_node_ids_before = mirage.nodes.get_active_node_ids()
    mirage.nodes.register_active(ip=ip, port=port)
    active_node_ids_after = mirage.nodes.get_active_node_ids()

    assert len(active_node_ids_after) == len(active_node_ids_before) + 1

    mirage.wallet = main_wallet


def test_get_by_address(mirage, node_wallets):
    main_wallet = mirage.wallet
    mirage.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()

    mirage.nodes.register_active(ip=ip, port=port)
    node = mirage.nodes.get_by_address(mirage.wallet.address)

    assert node is not None
    assert node.address == mirage.wallet.address
    assert node.ip_str == ip
    assert node.port == port

    with pytest.raises(ContractLogicError):
        mirage.nodes.get_by_address(node_wallets[1].address)

    mirage.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [1])
def test_active_node_exists(mirage, node_wallets):
    main_wallet = mirage.wallet
    mirage.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()

    mirage.nodes.register_active(ip=ip, port=port)
    node = mirage.nodes.get_by_address(mirage.wallet.address)
    node_id = node.id

    assert mirage.nodes.active_node_exists(node_id) is True
    assert mirage.nodes.active_node_exists(999) is False

    mirage.wallet = main_wallet


def test_decode_public_key(mirage):
    raw_public_key = [b'\x12\x34\x56\x78', b'\x9a\xbc\xde\xf0']
    decoded = mirage.nodes.decode_public_key(raw_public_key)

    assert isinstance(decoded, str)
    assert decoded.startswith('0x')
    assert len(decoded) == 18
