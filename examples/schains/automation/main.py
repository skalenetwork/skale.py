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
""" SKALE chain automation """

import datetime
import json
import logging
import os
import sys

import skale.utils.helper as Helper
from examples.schains.automation.config import (ETH_AMOUNT, FOLDER_NAME,
                                                LONG_LINE, NUMBER_OF_ACCOUNTS,
                                                SKALE_AMOUNT)
from skale import BlockchainEnv, Skale
from skale.utils.account_tools import (check_ether_balance,
                                       check_skale_balance, generate_account,
                                       init_wallet, send_ether, send_tokens)
from tests.utils import generate_random_schain_data

Helper.init_default_logger()
logger = logging.getLogger(__name__)


def get_filename(i, schain_name=''):
    time = datetime.datetime.now()
    return f'wallet_{i}_{schain_name}_{time}.json'


def save_info(filename, schain_info=None, wallet=None):
    info = {
        'schain_info': schain_info,
        'wallet': wallet
    }

    filepath = os.path.join(FOLDER_NAME, filename)
    with open(filepath, 'w') as outfile:
        logger.info(f'Saving info to {filename}')
        json.dump(info, outfile, indent=4)


def create_schain(skale, wallet):
    type_of_nodes, lifetime_seconds, name = generate_random_schain_data()
    price_in_wei = skale.schains.get_schain_price(type_of_nodes, lifetime_seconds)

    res = skale.manager.create_schain(lifetime_seconds, type_of_nodes, price_in_wei, name, wallet)
    receipt = Helper.await_receipt(skale.web3, res['tx'])
    Helper.check_receipt(receipt)

    schain_struct = skale.schains_data.get_by_name(name)
    schain_nodes = skale.schains_data.get_nodes_for_schain_config(name)
    return {'schain_struct': schain_struct, 'schain_nodes': schain_nodes}


def generate_accounts(skale, base_wallet, n, debug=True):
    for i in range(0, n):
        wallet = generate_account(skale.web3)

        send_tokens(skale, base_wallet, wallet['address'], SKALE_AMOUNT, debug)
        send_ether(skale.web3, base_wallet, wallet['address'], ETH_AMOUNT, debug)

        if debug:
            check_ether_balance(skale.web3, wallet['address'])
            check_skale_balance(skale, wallet['address'])

        schain_info = create_schain(skale, wallet)

        filename = get_filename(i, schain_info['schain_struct']['name'])
        save_info(filename, schain_info, wallet)

        logger.info(LONG_LINE)


if __name__ == "__main__":
    skale = Skale(BlockchainEnv.DO)
    base_wallet = init_wallet()
    amount = sys.argv[1] or NUMBER_OF_ACCOUNTS
    generate_accounts(skale, base_wallet, int(amount))
