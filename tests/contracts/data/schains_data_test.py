#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" SKALE chain data test """

import skale.contracts.data.nodes_data as nodes_data
from skale.contracts.data.nodes_data import SCHAIN_CONFIG_FIELDS
from skale.contracts.data.schains_data import FIELDS, PORTS_PER_SCHAIN
from tests.constants import DEFAULT_SCHAIN_ID, NOT_EXIST_SCHAIN_ID, EMPTY_SCHAIN_ARR, \
    DEFAULT_SCHAIN_NAME, \
    MIN_NODES_IN_SCHAIN, DEFAULT_NODE_ID, DEFAULT_NODE_PORT, NOT_EXIST_SCHAIN_NAME, \
    DEFAULT_SCHAIN_INDEX


def test_get_raw(skale):
    schain_arr = skale.schains_data._SChainsData__get_raw(DEFAULT_SCHAIN_ID)
    assert len(FIELDS) == len(schain_arr)


def test_get_raw_not_exist(skale):
    schain_arr = skale.schains_data._SChainsData__get_raw(NOT_EXIST_SCHAIN_ID)
    assert schain_arr == EMPTY_SCHAIN_ARR


def test_get(skale):
    schain = skale.schains_data.get(DEFAULT_SCHAIN_ID)
    assert list(schain.keys()) == FIELDS
    assert [k for k, v in schain.items() if v is None] == []


def test_get_by_name(skale):
    schain = skale.schains_data.get(DEFAULT_SCHAIN_ID)
    schain_name = schain['name']

    schain_by_name = skale.schains_data.get_by_name(schain_name)
    assert list(schain_by_name.keys()) == FIELDS
    assert schain == schain_by_name


def test_get_schains_for_owner(skale, wallet, empty_wallet):
    schains = skale.schains_data.get_schains_for_owner(wallet['address'])

    assert isinstance(schains, list)
    assert set(schains[-1].keys()) == set(FIELDS)


def test_get_schain_list_size(skale, wallet, empty_wallet):
    list_size = skale.schains_data.get_schain_list_size(wallet['address'])
    empty_list_size = skale.schains_data.get_schain_list_size(empty_wallet.address)

    assert list_size != 0
    assert empty_list_size == 0


def test_get_schain_id_by_index_for_owner(skale, wallet):
    schain_id = skale.schains_data.get_schain_id_by_index_for_owner(wallet['address'], 0)
    schain = skale.schains_data.get(schain_id)

    assert schain['owner'] == wallet['address']


def test_get_nodes_for_schain_config(skale):
    schain_nodes = skale.schains_data.get_nodes_for_schain_config(DEFAULT_SCHAIN_NAME)

    assert len(schain_nodes) >= MIN_NODES_IN_SCHAIN

    print(schain_nodes[0].keys())
    print(SCHAIN_CONFIG_FIELDS)

    assert set(schain_nodes[0].keys()) == set(SCHAIN_CONFIG_FIELDS)


def test_get_schain_base_port_on_node(skale):
    schain_port_on_node = skale.schains_data.get_schain_base_port_on_node(
        DEFAULT_SCHAIN_NAME,
        DEFAULT_NODE_ID,
        DEFAULT_NODE_PORT
    )

    # todo: this will fail if default schain is not the first one on default node
    assert schain_port_on_node == DEFAULT_NODE_PORT
    # todo: think about more checks


def test_get_schain_index_in_node(skale):
    node_schains = skale.schains_data.get_schains_for_node(DEFAULT_NODE_ID)
    schain_index_in_node = skale.schains_data.get_schain_index_in_node(DEFAULT_SCHAIN_NAME,
                                                                       node_schains)
    not_exist_schain_index_in_node = skale.schains_data.get_schain_index_in_node(
        NOT_EXIST_SCHAIN_NAME, node_schains)

    assert schain_index_in_node != -1
    assert not_exist_schain_index_in_node == -1


def test_calc_schain_base_port(skale):
    schain_base_port = skale.schains_data.calc_schain_base_port(DEFAULT_NODE_PORT,
                                                                DEFAULT_SCHAIN_INDEX)
    schain_base_port_next = skale.schains_data.calc_schain_base_port(DEFAULT_NODE_PORT,
                                                                     DEFAULT_SCHAIN_INDEX + 1)

    schain_base_port_calc = schain_base_port + ((DEFAULT_SCHAIN_INDEX + 1) * PORTS_PER_SCHAIN)

    assert schain_base_port == DEFAULT_NODE_PORT
    assert schain_base_port_calc == schain_base_port_next


def test_get_nodes_for_schain(skale):
    schain_nodes = skale.schains_data.get_nodes_for_schain(DEFAULT_SCHAIN_NAME)
    fields_with_id = nodes_data.FIELDS.copy()
    fields_with_id.append('id')

    assert len(schain_nodes) >= MIN_NODES_IN_SCHAIN
    assert list(schain_nodes[0].keys()) == fields_with_id


def test_get_node_ids_for_schain(skale):
    schain_node_ids = skale.schains_data.get_node_ids_for_schain(DEFAULT_SCHAIN_NAME)

    assert isinstance(schain_node_ids, list)
    assert len(schain_node_ids) >= MIN_NODES_IN_SCHAIN


def test_get_schain_ids_for_node(skale):
    schain_ids_for_node = skale.schains_data.get_schain_ids_for_node(DEFAULT_NODE_ID)

    assert isinstance(schain_ids_for_node, list)
    assert len(schain_ids_for_node) > 0


def test_get_schains_for_node(skale):
    schains_for_node = skale.schains_data.get_schains_for_node(DEFAULT_NODE_ID)
    schain_ids_for_node = skale.schains_data.get_schain_ids_for_node(DEFAULT_NODE_ID)

    assert isinstance(schains_for_node, list)
    assert len(schains_for_node) > 0
    assert len(schains_for_node) == len(schain_ids_for_node)

    test_schain = schains_for_node[0]
    schain_node_ids = skale.schains_data.get_node_ids_for_schain(test_schain['name'])

    assert DEFAULT_NODE_ID in schain_node_ids


def test_name_to_id(skale):
    schain_id = skale.schains_data.name_to_id(DEFAULT_SCHAIN_NAME)

    assert schain_id == DEFAULT_SCHAIN_ID


def test_get_all_schains_ids(skale):
    schains_ids = skale.schains_data.get_all_schains_ids()
    schain = skale.schains_data.get(schains_ids[-1])
    assert list(schain.keys()) == FIELDS
