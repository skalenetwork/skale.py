""" SKALE chain test """

from dataclasses import fields
from hexbytes import HexBytes
from web3 import Web3

from skale.contracts.manager.schains import FIELDS, SchainStructure
from skale.dataclasses.schain_options import SchainOptions
from skale.utils.contracts_provision.fake_multisig_contract import FAKE_MULTISIG_DATA_PATH
from skale.utils.contracts_provision.main import generate_random_schain_data, create_schain
from skale.utils.helper import get_abi
from skale.wallets.web3_wallet import generate_wallet

from tests.constants import (DEFAULT_NODE_NAME, DEFAULT_SCHAIN_ID,
                             DEFAULT_SCHAIN_NAME, LIFETIME_SECONDS)


def test_get(skale):
    schain = skale.schains.get(DEFAULT_SCHAIN_ID)
    assert isinstance(schain, SchainStructure)
    assert isinstance(schain.options, SchainOptions)


def test_get_by_name(skale):
    schain = skale.schains.get(DEFAULT_SCHAIN_ID)
    schain_name = schain.name

    schain_by_name = skale.schains.get_by_name(schain_name)
    assert [field.name for field in fields(schain_by_name)] == FIELDS
    assert schain == schain_by_name


def test_get_schains_for_owner(skale, schain, empty_account):
    schains = skale.schains.get_schains_for_owner(skale.wallet.address)
    assert isinstance(schains, list)
    assert len(schains) > 0
    assert set([field.name for field in fields(schains[-1])]) == set(FIELDS)

    schains = skale.schains.get_schains_for_owner(empty_account.address)
    assert schains == []


def test_get_schains_for_node(skale, schain):
    node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
    schains_for_node = skale.schains.get_schains_for_node(node_id)
    schain_ids_for_node = skale.schains_internal.get_schain_ids_for_node(
        node_id
    )

    assert isinstance(schains_for_node, list)
    assert len(schains_for_node) > 0
    assert len(schains_for_node) == len(schain_ids_for_node)

    test_schain = schains_for_node[0]
    schain_node_ids = skale.schains_internal.get_node_ids_for_schain(
        test_schain.name
    )

    assert node_id in schain_node_ids


def test_name_to_id(skale):
    schain_id = skale.schains.name_to_id(DEFAULT_SCHAIN_NAME)
    assert schain_id == Web3.to_bytes(hexstr=DEFAULT_SCHAIN_ID)


def test_get_all_schains_ids(skale, schain):
    schains_ids = skale.schains_internal.get_all_schains_ids()
    schain = skale.schains.get(schains_ids[-1])
    assert [field.name for field in fields(schain)] == FIELDS


def test_get_schain_price(skale):
    schain_price = skale.schains.get_schain_price(1, LIFETIME_SECONDS)
    assert schain_price > 0
    assert type(schain_price) is int


def test_add_schain_by_foundation(skale, nodes):
    skale.schains.grant_role(
        skale.schains.schain_creator_role(),
        skale.wallet.address
    )
    _, lifetime_seconds, name = generate_random_schain_data(skale)
    type_of_nodes = 1  # test2 schain
    try:
        skale.schains.add_schain_by_foundation(
            lifetime_seconds, type_of_nodes, 0, name
        )
        schains_ids_after = skale.schains_internal.get_all_schains_ids()
        schains_names = [
            skale.schains.get(sid).name
            for sid in schains_ids_after
        ]
        assert name in schains_names
        new_schain = skale.schains.get_by_name(name)
        assert new_schain.mainnetOwner == skale.wallet.address
    finally:
        skale.manager.delete_schain(name, wait_for=True)

    schains_ids_after = skale.schains_internal.get_all_schains_ids()

    schains_names = [
        skale.schains.get(sid).name
        for sid in schains_ids_after
    ]
    assert name not in schains_names


def test_add_schain_by_foundation_with_options(skale, nodes):
    skale.schains.grant_role(
        skale.schains.schain_creator_role(),
        skale.wallet.address
    )
    _, lifetime_seconds, name = generate_random_schain_data(skale)
    type_of_nodes = 1  # test2 schain
    try:
        skale.schains.add_schain_by_foundation(
            lifetime_seconds,
            type_of_nodes,
            0,
            name,
            options=SchainOptions(
                multitransaction_mode=True,
                threshold_encryption=False
            ),
            wait_for=True
        )
        schain = skale.schains.get_by_name(name)

        assert schain.options.multitransaction_mode is True
        assert schain.options.threshold_encryption is False
    finally:
        skale.manager.delete_schain(name)


def test_add_schain_by_foundation_custom_owner(skale, nodes):
    skale.schains.grant_role(
        skale.schains.schain_creator_role(),
        skale.wallet.address
    )
    _, lifetime_seconds, name = generate_random_schain_data(skale)
    type_of_nodes = 1  # test2 schain
    main_wallet = skale.wallet
    custom_wallet = generate_wallet(skale.web3)
    try:
        skale.schains.add_schain_by_foundation(
            lifetime_seconds,
            type_of_nodes,
            0,
            name,
            schain_owner=custom_wallet.address,
            wait_for=True
        )

        new_schain = skale.schains.get_by_name(name)
        assert new_schain.mainnetOwner != skale.wallet.address
        assert new_schain.mainnetOwner == custom_wallet.address

        skale.wallet = custom_wallet
    finally:
        skale.wallet = main_wallet
        skale.manager.delete_schain_by_root(name, wait_for=True)

    schains_ids_after = skale.schains_internal.get_all_schains_ids()

    schains_names = [
        skale.schains.get(sid).name
        for sid in schains_ids_after
    ]
    assert name not in schains_names


def test_add_schain_by_foundation_custom_originator(skale, nodes):
    skale.schains.grant_role(
        skale.schains.schain_creator_role(),
        skale.wallet.address
    )
    _, lifetime_seconds, name = generate_random_schain_data(skale)
    type_of_nodes = 1  # test2 schain
    custom_originator = generate_wallet(skale.web3)

    fake_multisig_data = get_abi(FAKE_MULTISIG_DATA_PATH)
    payable_contract_address = fake_multisig_data['address']

    try:
        skale.schains.add_schain_by_foundation(
            lifetime_seconds,
            type_of_nodes,
            0,
            name,
            schain_owner=payable_contract_address,
            schain_originator=custom_originator.address
        )
        new_schain = skale.schains.get_by_name(name)

        assert new_schain.originator != skale.wallet.address
        assert new_schain.originator == custom_originator.address

    finally:
        if name:
            skale.manager.delete_schain_by_root(name)

        schains_ids_after = skale.schains_internal.get_all_schains_ids()

    schains_names = [
        skale.schains.get(sid).name
        for sid in schains_ids_after
    ]
    assert name not in schains_names


def test_get_active_schains_for_node(skale, nodes, schain):
    name = None
    try:
        name = create_schain(skale, random_name=True)
        node_id = skale.nodes.node_name_to_index(DEFAULT_NODE_NAME)
        active_schains = skale.schains.get_active_schains_for_node(node_id)
        all_schains = skale.schains.get_schains_for_node(node_id)
        all_active_schains = [
            schain for schain in all_schains if schain.active]
        for active_schain in all_active_schains:
            assert active_schain in active_schains
    finally:
        if name:
            skale.manager.delete_schain_by_root(name)


def test_name_to_group_id(skale):
    name = 'TEST'
    gid = skale.schains.name_to_group_id(name)
    assert gid == HexBytes('0x852daa74cc3c31fe64542bb9b8764cfb91cc30f9acf9389071ffb44a9eefde46')  # noqa


def test_get_options(skale, nodes):
    schain_options = SchainOptions(
        multitransaction_mode=True,
        threshold_encryption=False
    )
    name = None
    try:
        name = create_schain(skale, random_name=True,
                             schain_options=schain_options)
        id_ = skale.schains.name_to_id(name)
        options = skale.schains.get_options(id_)
        assert options == schain_options
        options = skale.schains.get_options_by_name(name)
        assert options == schain_options
        raw_options = skale.schains._SChains__raw_get_options(id_)
        assert raw_options == [('multitr', b'\x01'), ('encrypt', b'\x00')]

    finally:
        if name:
            skale.manager.delete_schain(name)


def test_restart_schain_creation(skale, nodes, schain):
    name = schain
    skale.schains.restart_schain_creation(name)
