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
""" Create SKALE chain example """

import skale.utils.helper as Helper
from skale import BlockchainEnv, Skale
from skale.utils.account_tools import init_wallet
from tests.utils import generate_random_schain_data

Helper.init_default_logger()


def create_schain(skale, wallet):
    type_of_nodes, lifetime_seconds, name = generate_random_schain_data()
    price_in_wei = skale.schains.get_schain_price(type_of_nodes, lifetime_seconds)

    res = skale.manager.create_schain(lifetime_seconds, type_of_nodes, price_in_wei, name, wallet)
    receipt = Helper.await_receipt(skale.web3, res['tx'])
    Helper.check_receipt(receipt)
    return receipt


if __name__ == "__main__":
    skale = Skale(BlockchainEnv.DO)
    wallet = init_wallet()
    res = create_schain(skale, wallet)
    print('sChain created')
