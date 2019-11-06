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
""" SKALE data prep for testing """

import click

import skale.utils.helper as Helper
from skale import Skale
from skale.utils.account_tools import init_test_wallet
from skale.utils.web3_utils import wait_receipt, check_receipt
from tests.constants import (DEFAULT_SCHAIN_NAME, DEFAULT_NODE_NAME,
                             ENDPOINT, TEST_ABI_FILEPATH)
from tests.utils import generate_random_node_data, generate_random_schain_data


def cleanup_nodes_schains(skale, wallet):
    print('Cleanup nodes and schains')
    for schain_id in skale.schains_data.get_all_schains_ids():
        schain_data = skale.schains_data.get(schain_id)
        schain_name = schain_data.get('name', None)
        if schain_name is not None:
            res = skale.manager.delete_schain(schain_name, wallet)
            receipt = wait_receipt(skale.web3, res['tx'])
            check_receipt(receipt)
    for node_id in skale.nodes_data.get_active_node_ids():
        res = skale.manager.deregister(node_id, wallet)
        receipt = wait_receipt(skale.web3, res['tx'])
        check_receipt(receipt)


def create_nodes(skale, wallet):
    # create couple of nodes
    print('Creating two nodes')
    node_names = [DEFAULT_NODE_NAME, 'test_node_2']
    for name in node_names:
        ip, public_ip, port, _ = generate_random_node_data()
        res = skale.manager.create_node(ip, port, name, wallet, public_ip)
        receipt = wait_receipt(skale.web3, res['tx'])
        check_receipt(receipt)


def create_schain(skale, wallet):
    print('Creating schain')
    # create 1 s-chain
    type_of_nodes, lifetime_seconds, _ = generate_random_schain_data()
    price_in_wei = skale.schains.get_schain_price(type_of_nodes, lifetime_seconds)

    res = skale.manager.create_schain(
        lifetime_seconds,
        type_of_nodes,
        price_in_wei,
        DEFAULT_SCHAIN_NAME,
        wallet
    )
    receipt = wait_receipt(skale.web3, res['tx'])
    check_receipt(receipt)


@click.command()
@click.option('--cleanup-only', is_flag=True)
def prepare_data(cleanup_only):
    Helper.init_default_logger()
    skale = Skale(ENDPOINT, TEST_ABI_FILEPATH)
    wallet = init_test_wallet()
    cleanup_nodes_schains(skale, wallet)
    if not cleanup_only:
        try:
            create_nodes(skale, wallet)
            create_schain(skale, wallet)
        except Exception as err:
            cleanup_nodes_schains(skale, wallet)
            raise err


if __name__ == "__main__":
    prepare_data()
