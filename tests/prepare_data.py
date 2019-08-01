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

import skale.utils.helper as Helper
from skale import Skale
from skale.utils.account_tools import init_test_wallet
from tests.constants import DEFAULT_SCHAIN_NAME, TEST_NAME, ENDPOINT, TEST_ABI_FILEPATH
from tests.utils import generate_random_node_data, generate_random_schain_data


def prepare_data(skale, wallet):
    # create couple of nodes
    for i in range(0, 2):
        ip, public_ip, port, name = generate_random_node_data()
        if (i == 0):
            name = TEST_NAME
        res = skale.manager.create_node(ip, port, name, wallet, public_ip)
        receipt = Helper.await_receipt(skale.web3, res['tx'])
        Helper.check_receipt(receipt)

    # create 1 s-chain
    type_of_nodes, lifetime_seconds, name = generate_random_schain_data()
    price_in_wei = skale.schains.get_schain_price(type_of_nodes, lifetime_seconds)
    res = skale.manager.create_schain(
        lifetime_seconds,
        type_of_nodes,
        price_in_wei,
        DEFAULT_SCHAIN_NAME,
        wallet
    )
    receipt = Helper.await_receipt(skale.web3, res['tx'])
    Helper.check_receipt(receipt)


if __name__ == "__main__":
    Helper.init_default_logger()
    skale = Skale(ENDPOINT, TEST_ABI_FILEPATH)
    wallet = init_test_wallet()

    prepare_data(skale, wallet)
