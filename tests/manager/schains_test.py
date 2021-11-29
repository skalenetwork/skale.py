""" SKALE chain test """

from hexbytes import HexBytes

from skale.contracts.manager.schains import FIELDS, SchainStructure
from skale.utils.contracts_provision.fake_multisig_contract import FAKE_MULTISIG_DATA_PATH
from skale.transactions.tools import send_eth_with_skale
from tests.constants import (DEFAULT_NODE_NAME, DEFAULT_SCHAIN_ID,
                             DEFAULT_SCHAIN_NAME, LIFETIME_SECONDS)

from skale.utils.contracts_provision.main import generate_random_schain_data, create_schain
from skale.wallets.web3_wallet import generate_wallet
from skale.utils.helper import get_abi


def test_get(skale):
    schain = skale.schains.get(DEFAULT_SCHAIN_ID)
    assert list(schain.keys()) == FIELDS
    assert [k for k, v in schain.items() if v is None] == []


def test_get_object(skale):
    schain = skale.schains.get(DEFAULT_SCHAIN_ID, obj=True)
    assert isinstance(schain, SchainStructure)


def test_get_by_name(skale):
    schain = skale.schains.get(DEFAULT_SCHAIN_ID)
    schain_name = schain['name']

    schain_by_name = skale.schains.get_by_name(schain_name)
    assert list(schain_by_name.keys()) == FIELDS
    assert schain == schain_by_name


def test_get_schains_for_owner(skale, empty_account):
    schains = skale.schains.get_schains_for_owner(skale.wallet.address)

    assert isinstance(schains, list)
    assert set(schains[-1].keys()) == set(FIELDS)


def test_get_schains_for_node(skale):
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    schains_for_node = skale.schains.get_schains_for_node(node_id)
    schain_ids_for_node = skale.schains_internal.get_schain_ids_for_node(node_id)

    assert isinstance(schains_for_node, list)
    assert len(schains_for_node) > 0
    assert len(schains_for_node) == len(schain_ids_for_node)

    test_schain = schains_for_node[0]
    schain_node_ids = skale.schains_internal.get_node_ids_for_schain(
        test_schain['name'])

    assert node_id in schain_node_ids


def test_name_to_id(skale):
    schain_id = skale.schains.name_to_id(DEFAULT_SCHAIN_NAME)
    assert schain_id == DEFAULT_SCHAIN_ID


def test_get_all_schains_ids(skale):
    schains_ids = skale.schains_internal.get_all_schains_ids()
    schain = skale.schains.get(schains_ids[-1])
    assert list(schain.keys()) == FIELDS


def test_get_schain_price(skale):
    schain_price = skale.schains.get_schain_price(1, LIFETIME_SECONDS)
    assert schain_price > 0
    assert type(schain_price) is int


def test_add_schain_by_foundation(skale):
    skale.schains.grant_role(skale.schains.schain_creator_role(),
                             skale.wallet.address)
    type_of_nodes, lifetime_seconds, name = generate_random_schain_data(skale)
    skale.schains.add_schain_by_foundation(
        lifetime_seconds, type_of_nodes, 0, name, wait_for=True
    )

    schains_ids_after = skale.schains_internal.get_all_schains_ids()

    schains_names = [
        skale.schains.get(sid)['name']
        for sid in schains_ids_after
    ]
    assert name in schains_names

    new_schain = skale.schains.get_by_name(name)
    assert new_schain['mainnetOwner'] == skale.wallet.address

    skale.manager.delete_schain(name, wait_for=True)

    schains_ids_after = skale.schains_internal.get_all_schains_ids()

    schains_names = [
        skale.schains.get(sid)['name']
        for sid in schains_ids_after
    ]
    assert name not in schains_names


def test_add_schain_by_foundation_custom_owner(skale):
    skale.schains.grant_role(skale.schains.schain_creator_role(),
                             skale.wallet.address)
    type_of_nodes, lifetime_seconds, name = generate_random_schain_data(skale)
    custom_wallet = generate_wallet(skale.web3)
    skale.schains.add_schain_by_foundation(
        lifetime_seconds, type_of_nodes, 0, name, custom_wallet.address, wait_for=True
    )

    new_schain = skale.schains.get_by_name(name)
    assert new_schain['mainnetOwner'] != skale.wallet.address
    assert new_schain['mainnetOwner'] == custom_wallet.address

    send_eth_with_skale(skale, custom_wallet.address, 10 ** 18)
    skale.wallet = custom_wallet
    skale.manager.delete_schain(name, wait_for=True)

    schains_ids_after = skale.schains_internal.get_all_schains_ids()

    schains_names = [
        skale.schains.get(sid)['name']
        for sid in schains_ids_after
    ]
    assert name not in schains_names


def test_add_schain_by_foundation_custom_erector(skale):
    skale.schains.grant_role(skale.schains.schain_creator_role(),
                             skale.wallet.address)
    type_of_nodes, lifetime_seconds, name = generate_random_schain_data(skale)
    custom_erector = generate_wallet(skale.web3)

    fake_multisig_data = get_abi(FAKE_MULTISIG_DATA_PATH)
    payable_contract_address = fake_multisig_data['address']

    skale.schains.add_schain_by_foundation(
        lifetime_seconds, type_of_nodes, 0, name,
        schain_owner=payable_contract_address, schain_erector=custom_erector.address
    )
    new_schain = skale.schains.get_by_name(name)

    assert new_schain['erector'] != skale.wallet.address
    assert new_schain['erector'] == custom_erector.address

    send_eth_with_skale(skale, custom_erector.address, 10 ** 18)
    skale.manager.delete_schain_by_root(name)

    schains_ids_after = skale.schains_internal.get_all_schains_ids()

    schains_names = [
        skale.schains.get(sid)['name']
        for sid in schains_ids_after
    ]
    assert name not in schains_names


def test_get_active_schains_for_node(skale):
    create_schain(skale, 'test1')
    create_schain(skale, 'test2')
    skale.manager.delete_schain('test1', wait_for=True)

    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    active_schains = skale.schains.get_active_schains_for_node(node_id)
    all_schains = skale.schains.get_schains_for_node(node_id)
    all_active_schains = [schain for schain in all_schains if schain['active']]
    for active_schain in all_active_schains:
        assert active_schain in active_schains


def test_name_to_group_id(skale):
    name = 'TEST'
    gid = skale.schains.name_to_group_id(name)
    assert gid == HexBytes('0x852daa74cc3c31fe64542bb9b8764cfb91cc30f9acf9389071ffb44a9eefde46')  # noqa
