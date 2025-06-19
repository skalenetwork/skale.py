import pytest

from web3.exceptions import ContractLogicError

from skale.utils.contracts_provision.utils import generate_random_node_data


@pytest.mark.parametrize('number_of_nodes', [1])
def test_get_node(mirage, mirage_active_nodes):
    registered_node = mirage.nodes.get_by_address(mirage_active_nodes[0].address)
    node_id = registered_node.id

    node = mirage.nodes.get(node_id)

    assert node is not None
    assert node.id == node_id
    assert node.address == mirage_active_nodes[0].address
    assert isinstance(node.ip_str, str)
    assert isinstance(node.port, int)
    assert node.name == f'node-{node_id}'
    assert isinstance(node.public_key, str)
    assert node.public_key.startswith('0x')


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
def test_set_domain_name(mirage, mirage_active_nodes):
    main_wallet = mirage.wallet
    mirage.wallet = mirage_active_nodes[0]

    node = mirage.nodes.get_by_address(mirage_active_nodes[0].address)
    node_id = node.id

    domain_name = 'test-domain.example.com'
    mirage.nodes.set_domain_name(node_id, domain_name)

    updated_node = mirage.nodes.get(node_id)
    assert updated_node.domain_name == domain_name

    mirage.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [1])
def test_set_ip_address(mirage, mirage_active_nodes):
    main_wallet = mirage.wallet
    mirage.wallet = mirage_active_nodes[0]

    node = mirage.nodes.get_by_address(mirage_active_nodes[0].address)
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

    committee_contract = mirage.nodes.contract.functions.committeeContract().call()
    assert committee_contract == committee_address

    mirage.nodes.set_committee(original_committee_address)


@pytest.mark.parametrize('number_of_nodes', [2])
def test_request_change_owner(mirage, mirage_passive_nodes):
    main_wallet = mirage.wallet

    node_id = mirage.nodes.get_passive_node_ids_for_address(mirage_passive_nodes[0].address)[0]
    change_requests_for_node = mirage.nodes.contract.functions.ownerChangeRequests(node_id).call()

    assert change_requests_for_node == '0x0000000000000000000000000000000000000000'

    new_owner = mirage_passive_nodes[1].address

    mirage.wallet = mirage_passive_nodes[0]
    mirage.nodes.request_change_owner(node_id, new_owner)

    updated_change_requests_for_node = mirage.nodes.contract.functions.ownerChangeRequests(
        node_id
    ).call()
    assert updated_change_requests_for_node == new_owner

    mirage.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [2])
def test_confirm_owner_change(mirage, mirage_passive_nodes):
    main_wallet = mirage.wallet

    node_id = mirage.nodes.get_passive_node_ids_for_address(mirage_passive_nodes[0].address)[0]
    new_owner = mirage_passive_nodes[1].address

    mirage.wallet = mirage_passive_nodes[0]
    mirage.nodes.request_change_owner(node_id, new_owner)

    change_requests_for_node = mirage.nodes.contract.functions.ownerChangeRequests(node_id).call()
    assert change_requests_for_node == new_owner

    mirage.wallet = mirage_passive_nodes[1]
    mirage.nodes.confirm_owner_change(node_id)

    change_requests_for_node_after_confirm = mirage.nodes.contract.functions.ownerChangeRequests(
        node_id
    ).call()
    assert change_requests_for_node_after_confirm == '0x0000000000000000000000000000000000000000'

    mirage.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [1])
def test_get_id(mirage, mirage_active_nodes):
    node_id = mirage.nodes.get_id(mirage_active_nodes[0].address)
    assert node_id > 0

    node = mirage.nodes.get(node_id)
    assert node is not None
    assert node.address == mirage_active_nodes[0].address


@pytest.mark.parametrize('number_of_nodes', [2])
def test_get_passive_node_ids_for_address(mirage, mirage_passive_nodes):
    node_ids_first = mirage.nodes.get_passive_node_ids_for_address(mirage_passive_nodes[0].address)
    node_ids_second = mirage.nodes.get_passive_node_ids_for_address(mirage_passive_nodes[1].address)
    assert len(node_ids_first) == 1
    assert node_ids_first[0] > 0
    assert len(node_ids_second) == 1
    assert node_ids_second[0] > 0

    main_wallet = mirage.wallet
    mirage.wallet = mirage_passive_nodes[0]
    ip, _, port, _ = generate_random_node_data()

    mirage.nodes.register_passive(ip=ip, port=port)

    node_ids_first = mirage.nodes.get_passive_node_ids_for_address(mirage_passive_nodes[0].address)
    node_ids_second = mirage.nodes.get_passive_node_ids_for_address(mirage_passive_nodes[1].address)
    assert len(node_ids_first) == 2
    assert node_ids_first[0] > 0
    assert node_ids_first[1] > 0
    assert len(node_ids_second) == 1
    assert node_ids_second[0] > 0

    mirage.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [1])
def test_get_passive_node_ids(mirage, mirage_passive_nodes):
    passive_node_ids = mirage.nodes.get_passive_node_ids()

    assert len(passive_node_ids) >= 1
    assert all(node_id > 0 for node_id in passive_node_ids)


@pytest.mark.parametrize('number_of_nodes', [1])
def test_get_active_node_ids(mirage, mirage_active_nodes):
    active_node_ids = mirage.nodes.get_active_node_ids()

    assert len(active_node_ids) >= 1
    assert all(node_id > 0 for node_id in active_node_ids)


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
def test_active_node_exists(mirage, mirage_active_nodes):
    node = mirage.nodes.get_by_address(mirage_active_nodes[0].address)
    node_id = node.id

    assert mirage.nodes.active_node_exists(node_id) is True
    assert mirage.nodes.active_node_exists(999) is False


def test_decode_public_key(mirage):
    raw_public_key = [b'\x12\x34\x56\x78', b'\x9a\xbc\xde\xf0']
    decoded = mirage.nodes.decode_public_key(raw_public_key)

    assert isinstance(decoded, str)
    assert decoded.startswith('0x')
    assert len(decoded) == 18
