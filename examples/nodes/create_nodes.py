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
""" Create SKALE node example """

import os
import sys

import skale.utils.helper as Helper
from skale import Skale
from skale.utils.account_tools import init_wallet
from skale.utils.constants import LONG_LINE
from tests.utils import generate_random_node_data

from examples.helper import ENDPOINT, LOCAL_ABI_FILEPATH

Helper.init_default_logger()


def create_node(skale, wallet):
    ip, public_ip, port, name = generate_random_node_data()
    res = skale.manager.create_node(ip, port, name, wallet, public_ip)
    receipt = Helper.await_receipt(skale.web3, res['tx'])
    return receipt


def create_nodes(skale, amount, wallet):
    for i in range(int(amount)):
        print(LONG_LINE)
        print(f'Creating {i+1}/{amount} node...')
        receipt = create_node(skale, wallet)
        Helper.check_receipt(receipt)


if __name__ == "__main__":
    amount = sys.argv[1]

    skale = Skale(ENDPOINT, LOCAL_ABI_FILEPATH)
    wallet = init_wallet()

    print(f'Creating {amount} nodes...')
    create_nodes(skale, amount, wallet)
