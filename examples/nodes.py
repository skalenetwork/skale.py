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
""" Commands to manage SKALE nodes """

import json
import os

import click

import skale.utils.helper as Helper
from skale.utils.helper import ip_from_bytes
from skale import Skale
from skale.utils.account_tools import init_wallet
from skale.utils.constants import LONG_LINE
from tests.utils import generate_random_node_data

from examples.helper import ENDPOINT, ABI_FILEPATH

Helper.init_default_logger()


def create_node(skale, wallet):
    ip, public_ip, port, name = generate_random_node_data()
    port = 10000
    res = skale.manager.create_node(ip, port, name, wallet, public_ip)
    receipt = Helper.await_receipt(skale.web3, res['tx'])
    return receipt


@click.group()
@click.option('--endpoint', default=ENDPOINT, help='Skale manager endpoint')
@click.option('--abi-filepath', default=ABI_FILEPATH, type=click.Path(),
              help='abi file')
@click.pass_context
def main(ctx, endpoint, abi_filepath):
    ctx.ensure_object(dict)
    ctx.obj['skale'] = Skale(endpoint, abi_filepath)


@main.command()
@click.argument('amount', default=1)
@click.pass_context
def create(ctx, amount):
    """ Command to create given amount of nodes """
    wallet = init_wallet()
    skale = ctx.obj['skale']

    print(f'Creating {amount} nodes...')
    for i in range(int(amount)):
        print(LONG_LINE)
        print(f'Creating {i+1}/{amount} node...')
        receipt = create_node(skale, wallet)
        Helper.check_receipt(receipt)


@main.command()
@click.option('--save-to', default='./schains-by-node',
              help='Directory to save full schains data by specific node')
@click.pass_context
def schains_by_node(ctx, save_to):
    """ Command that shows schains for active nodes """
    skale = ctx.obj['skale']

    schains = []
    sizes = []
    for node_id in skale.nodes_data.get_active_node_ids():
        node = skale.nodes_data.get(node_id)

        node_struct = {
            'name': node['name'],
            'ip': ip_from_bytes(node['ip']),
            'basePort': node['port'],
            'publicIP': ip_from_bytes(node['publicIP']),
        }

        schains_for_node = skale.schains_data.get_schains_for_node(node_id)
        schains.append({
            'schains': schains_for_node,
            'amount': len(schains_for_node),
            'node': node_struct
        })
        sizes.append(len(schains_for_node))

    if not os.path.exists(save_to):
        os.makedirs(save_to)

    filepath = os.path.join(save_to, 'schains_data.json')
    with open(filepath, 'w') as outfile:
        json.dump(schains, outfile)

    print('Schains on each node:')
    print(sizes)


@main.command()
@click.pass_context
def show(ctx):
    """ Command to show id name and ip of active nodes """
    skale = ctx.obj['skale']

    nodes_data = []
    for _id in skale.nodes_data.get_active_node_ids():
        data = skale.nodes_data.get(_id)
        name = data.get('name')
        ip = ip_from_bytes(data.get('ip'))
        nodes_data.append((_id, name, ip))
    print(nodes_data)


@main.command()
@click.argument('node-name')
@click.pass_context
def remove(ctx, node_name):
    """ Command to remove node spcified by name """
    skale = ctx.obj['skale']
    wallet = init_wallet()

    node_id = skale.nodes_data.node_name_to_index(node_name)
    res = skale.manager.delete_node_by_root(node_id, wallet)

    receipt = Helper.await_receipt(skale.web3, res['tx'])
    Helper.check_receipt(receipt)


if __name__ == "__main__":
    main()
