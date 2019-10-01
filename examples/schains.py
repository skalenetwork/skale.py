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
""" Commands to manage SKALE schains """

import datetime
import json
import logging
import os

import click

import skale.utils.helper as Helper
from skale import Skale
from skale.utils.account_tools import (check_ether_balance,
                                       check_skale_balance, generate_account,
                                       init_wallet as init_base_wallet,
                                       send_ether, send_tokens)
from skale.utils.constants import LONG_LINE, SchainType
from skale.utils.random_names.generator import generate_random_schain_name

from examples.helper import ENDPOINT, ABI_FILEPATH


Helper.init_default_logger()
logger = logging.getLogger(__name__)


@click.group()
@click.option('--endpoint', default=ENDPOINT, help='skale manager endpoint')
@click.option('--abi-filepath', default=ABI_FILEPATH, help='abi file')
@click.pass_context
def main(ctx, endpoint, abi_filepath):
    ctx.ensure_object(dict)
    ctx.obj['skale'] = Skale(endpoint, abi_filepath)


def save_info(schain_index, schain_info=None, wallet=None, data_dir=None):
    time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    schain_name = schain_info['schain_struct']['name']
    filename = f'wallet_{schain_index}_{schain_name}_{time}.json'
    info = {
        'schain_info': schain_info,
        'wallet': wallet
    }
    if data_dir:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        filepath = os.path.join(data_dir, filename)
        print(filepath)
        with open(filepath, 'w') as outfile:
            logger.info(f'Saving info to {filename}')
            json.dump(info, outfile, indent=4)


def create_schain(skale, wallet, nodes_type):
    lifetime_seconds = 12 * 3600  # 12 hours
    schain_name = generate_random_schain_name()
    price_in_wei = skale.schains.get_schain_price(nodes_type,
                                                  lifetime_seconds)

    res = skale.manager.create_schain(lifetime_seconds, nodes_type,
                                      price_in_wei, schain_name, wallet)
    receipt = Helper.await_receipt(skale.web3, res['tx'])
    Helper.check_receipt(receipt)

    schain_struct = skale.schains_data.get_by_name(schain_name)
    schain_nodes = skale.schains_data.get_nodes_for_schain_config(schain_name)
    return {'schain_struct': schain_struct, 'schain_nodes': schain_nodes}


def create_account(skale, skale_amount, eth_amount, debug=True):
    base_wallet = init_base_wallet()
    wallet = generate_account(skale.web3)

    send_tokens(skale, base_wallet, wallet['address'], skale_amount, debug)
    send_ether(skale.web3, base_wallet, wallet['address'], eth_amount, debug)

    if debug:
        check_ether_balance(skale.web3, wallet['address'])
        check_skale_balance(skale, wallet['address'])

    return wallet


def show_all_schain_ids(skale):
    schains_number = skale.schains_data.get_schains_number()
    print(f'There are {schains_number} schains')
    schains_ids = skale.schains_data.get_all_schains_ids()
    print(schains_ids)


@main.command()
@click.argument('amount', default=1)
@click.option('--type', default=SchainType.TEST2.name,
              type=click.Choice([n_type.name for n_type in SchainType],
                                case_sensitive=False),
              help='Nodes type (tiny/small/medium/test2/test4) for schain')
@click.option('--save-to', default='./creds',
              help='Directory to save schains data')
@click.option('--skale-amount', default=1000,
              help='Amount of skale to add to new accounts')
@click.option('--eth-amount', default=10,
              help='Amount of eth to add to new accounts')
@click.pass_context
def create(ctx, amount, type, save_to, skale_amount, eth_amount):
    """ Command that creates new accounts with schains """
    skale = ctx.obj['skale']
    nodes_type = SchainType[type.upper()]
    for i in range(amount):
        wallet = create_account(skale, skale_amount, eth_amount)
        schain_info = create_schain(skale, wallet, nodes_type)
        save_info(i, schain_info, wallet, save_to)
        logger.info(LONG_LINE)
    show_all_schain_ids(skale)


@main.command()
@click.argument('schain_name')
@click.pass_context
def remove(ctx, schain_name):
    skale = ctx.obj['skale']
    wallet = init_base_wallet()
    res = skale.manager.delete_schain(schain_name, wallet)
    receipt = Helper.await_receipt(skale.web3, res['tx'])
    Helper.check_receipt(receipt)
    print(f'sChain {schain_name} removed!')


@main.command()
@click.pass_context
def show(ctx):
    """ Command that show all schains ids """
    skale = ctx.obj['skale']
    show_all_schain_ids(skale)


if __name__ == "__main__":
    main()
