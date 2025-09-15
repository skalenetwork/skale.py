import pytest
from web3.exceptions import ContractLogicError

from skale.utils.contracts_provision.utils import generate_random_node_data


@pytest.mark.parametrize('number_of_nodes', [1])
def test_get_node(fair, fair_active_nodes):
    registered_node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = registered_node.id

    node = fair.nodes.get(node_id)

    assert node is not None
    assert node.id == node_id
    assert node.address == fair_active_nodes[0].address
    assert isinstance(node.ip_str, str)
    assert isinstance(node.port, int)
    assert node.name == f'node-{node_id}'


@pytest.mark.parametrize('number_of_nodes', [1])
def test_get_public_key(fair, fair_active_nodes):
    registered_node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = registered_node.id
    public_key = fair.nodes.get_public_key(node_id)
    assert isinstance(public_key, str)
    assert public_key.startswith('0x')


@pytest.mark.parametrize('number_of_nodes', [1])
def test_register_active_node(fair, node_wallets):
    main_wallet = fair.wallet
    fair.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()
    self_stake_requirement = fair.staking.self_stake_requirement()

    with pytest.raises(ContractLogicError):
        fair.nodes.get_by_address(fair.wallet.address)

    active_node_ids_before = fair.nodes.get_active_node_ids()
    fair.nodes.register_active(ip=ip, port=port, value=self_stake_requirement)
    active_node_ids_after = fair.nodes.get_active_node_ids()

    assert len(active_node_ids_after) == len(active_node_ids_before) + 1

    node = fair.nodes.get_by_address(fair.wallet.address)
    assert node.address == fair.wallet.address

    fair.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [1])
def test_register_passive_node(fair, node_wallets):
    main_wallet = fair.wallet
    fair.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()

    with pytest.raises(ContractLogicError):
        fair.nodes.get_passive_node_ids_for_address(fair.wallet.address)

    passive_node_ids_before = fair.nodes.get_passive_node_ids()
    fair.nodes.register_passive(ip=ip, port=port)
    passive_node_ids_after = fair.nodes.get_passive_node_ids()

    assert len(passive_node_ids_after) == len(passive_node_ids_before) + 1

    node_id = fair.nodes.get_passive_node_ids_for_address(fair.wallet.address)[0]
    assert node_id in passive_node_ids_after

    fair.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [1])
def test_set_domain_name(fair, fair_active_nodes):
    main_wallet = fair.wallet
    fair.wallet = fair_active_nodes[0]

    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id

    domain_name = 'test-domain.example.com'
    fair.nodes.set_domain_name(node_id, domain_name)

    updated_node = fair.nodes.get(node_id)
    assert updated_node.domain_name == domain_name

    fair.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [1])
def test_set_ip_address(fair, fair_active_nodes):
    main_wallet = fair.wallet
    fair.wallet = fair_active_nodes[0]

    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id

    new_ip, _, new_port, _ = generate_random_node_data()
    fair.nodes.set_ip_address(node_id, new_ip, new_port)

    updated_node = fair.nodes.get(node_id)
    assert updated_node.ip_str == new_ip
    assert updated_node.port == new_port

    fair.wallet = main_wallet


def test_set_committee(fair, node_wallets):
    original_committee_address = fair.committee.address
    committee_address = node_wallets[0].address
    fair.nodes.set_committee(committee_address)

    committee_contract = fair.nodes.contract.functions.committeeContract().call()
    assert committee_contract == committee_address

    fair.nodes.set_committee(original_committee_address)


@pytest.mark.parametrize('number_of_nodes', [2])
def test_request_change_owner(fair, fair_passive_nodes):
    main_wallet = fair.wallet

    node_id = fair.nodes.get_passive_node_ids_for_address(fair_passive_nodes[0].address)[0]
    change_requests_for_node = fair.nodes.contract.functions.ownerChangeRequests(node_id).call()

    assert change_requests_for_node == '0x0000000000000000000000000000000000000000'

    new_owner = fair_passive_nodes[1].address

    fair.wallet = fair_passive_nodes[0]
    fair.nodes.request_change_owner(node_id, new_owner)

    updated_change_requests_for_node = fair.nodes.contract.functions.ownerChangeRequests(
        node_id
    ).call()
    assert updated_change_requests_for_node == new_owner

    fair.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [2])
def test_confirm_owner_change(fair, fair_passive_nodes):
    main_wallet = fair.wallet

    node_id = fair.nodes.get_passive_node_ids_for_address(fair_passive_nodes[0].address)[0]
    new_owner = fair_passive_nodes[1].address

    fair.wallet = fair_passive_nodes[0]
    fair.nodes.request_change_owner(node_id, new_owner)

    change_requests_for_node = fair.nodes.contract.functions.ownerChangeRequests(node_id).call()
    assert change_requests_for_node == new_owner

    fair.wallet = fair_passive_nodes[1]
    fair.nodes.confirm_owner_change(node_id)

    change_requests_for_node_after_confirm = fair.nodes.contract.functions.ownerChangeRequests(
        node_id
    ).call()
    assert change_requests_for_node_after_confirm == '0x0000000000000000000000000000000000000000'

    fair.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [1])
def test_get_id(fair, fair_active_nodes):
    node_id = fair.nodes.get_id(fair_active_nodes[0].address)
    assert node_id > 0

    node = fair.nodes.get(node_id)
    assert node is not None
    assert node.address == fair_active_nodes[0].address


@pytest.mark.parametrize('number_of_nodes', [2])
def test_get_passive_node_ids_for_address(fair, fair_passive_nodes):
    node_ids_first = fair.nodes.get_passive_node_ids_for_address(fair_passive_nodes[0].address)
    node_ids_second = fair.nodes.get_passive_node_ids_for_address(fair_passive_nodes[1].address)
    assert len(node_ids_first) == 1
    assert node_ids_first[0] > 0
    assert len(node_ids_second) == 1
    assert node_ids_second[0] > 0

    main_wallet = fair.wallet
    fair.wallet = fair_passive_nodes[0]
    ip, _, port, _ = generate_random_node_data()

    fair.nodes.register_passive(ip=ip, port=port)

    node_ids_first = fair.nodes.get_passive_node_ids_for_address(fair_passive_nodes[0].address)
    node_ids_second = fair.nodes.get_passive_node_ids_for_address(fair_passive_nodes[1].address)
    assert len(node_ids_first) == 2
    assert node_ids_first[0] > 0
    assert node_ids_first[1] > 0
    assert len(node_ids_second) == 1
    assert node_ids_second[0] > 0

    fair.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [1])
def test_get_passive_node_ids(fair, fair_passive_nodes):
    passive_node_ids = fair.nodes.get_passive_node_ids()

    assert len(passive_node_ids) >= 1
    assert all(node_id > 0 for node_id in passive_node_ids)


@pytest.mark.parametrize('number_of_nodes', [1])
def test_get_active_node_ids(fair, fair_active_nodes):
    active_node_ids = fair.nodes.get_active_node_ids()

    assert len(active_node_ids) >= 1
    assert all(node_id > 0 for node_id in active_node_ids)


def test_get_by_address(fair, node_wallets):
    main_wallet = fair.wallet
    fair.wallet = node_wallets[0]
    ip, _, port, _ = generate_random_node_data()
    self_stake_requirement = fair.staking.self_stake_requirement()

    fair.nodes.register_active(ip=ip, port=port, value=self_stake_requirement)
    node = fair.nodes.get_by_address(fair.wallet.address)

    assert node is not None
    assert node.address == fair.wallet.address
    assert node.ip_str == ip
    assert node.port == port

    with pytest.raises(ContractLogicError):
        fair.nodes.get_by_address(node_wallets[1].address)

    fair.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [1])
def test_active_node_exists(fair, fair_active_nodes):
    node = fair.nodes.get_by_address(fair_active_nodes[0].address)
    node_id = node.id

    assert fair.nodes.active_node_exists(node_id) is True
    assert fair.nodes.active_node_exists(999) is False


@pytest.mark.parametrize('number_of_nodes', [1])
def test_passive_node_exists_and_owner_request(fair, fair_passive_nodes):
    node_id = fair.nodes.get_passive_node_ids_for_address(fair_passive_nodes[0].address)[0]
    assert fair.nodes.passive_node_exists(node_id) is True
    assert (
        fair.nodes.get_owner_change_request(node_id) == '0x0000000000000000000000000000000000000000'
    )


def test_committee_contract_accessor(fair):
    assert fair.nodes.committee_contract() == fair.committee.address


def test_decode_public_key(fair):
    raw_public_key = [b'\x12\x34\x56\x78', b'\x9a\xbc\xde\xf0']
    decoded = fair.nodes.decode_public_key(raw_public_key)

    assert isinstance(decoded, str)
    assert decoded.startswith('0x')
    assert len(decoded) == 18


@pytest.mark.parametrize('number_of_nodes', [1])
def test_delete_node(fair, fair_passive_nodes):
    main_wallet = fair.wallet

    node_id = fair.nodes.get_passive_node_ids_for_address(fair_passive_nodes[0].address)[0]

    passive_node_ids_before = fair.nodes.get_passive_node_ids()
    assert node_id in passive_node_ids_before

    fair.wallet = fair_passive_nodes[0]
    fair.nodes.delete_node(node_id)

    passive_node_ids_after = fair.nodes.get_passive_node_ids()
    assert node_id not in passive_node_ids_after
    assert len(passive_node_ids_after) == len(passive_node_ids_before) - 1

    fair.wallet = main_wallet


@pytest.mark.parametrize('number_of_nodes', [1])
def test_delete_node_by_foundation(fair, fair_passive_nodes):
    node_id = fair.nodes.get_passive_node_ids_for_address(fair_passive_nodes[0].address)[0]
    before = fair.nodes.get_passive_node_ids()
    assert node_id in before
    fair.nodes.delete_node_by_foundation(node_id)
    after = fair.nodes.get_passive_node_ids()
    assert node_id not in after
