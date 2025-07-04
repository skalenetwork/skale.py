#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2025-Present SKALE Labs
#
#   SKALE.py is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   SKALE.py is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with SKALE.py.  If not, see <https://www.gnu.org/licenses/>.

import logging
import os

from eth_typing import HexStr

from skale import SkaleManager
from skale.types.schain import SchainName
from skale.utils.account_tools import send_eth
from skale.utils.contracts_provision.main import (
    DEFAULT_DOMAIN_NAME,
    add_test2_schain_type,
    add_test4_schain_type,
    add_test_permissions,
    create_schain,
    setup_validator,
)
from skale.utils.contracts_provision.utils import generate_random_node_data
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet
from skale.wallets.web3_wallet import generate_wallets

logger = logging.getLogger(__name__)

TEST_ETH_AMOUNT = 1
NODES_IN_SCHAIN = 4
CHAIN_NAME = SchainName('mirage')


def transfer_eth_to_wallets(skale, wallets):
    logger.info(f'Transfering {TEST_ETH_AMOUNT} ETH to {len(wallets)} test wallets')
    for wallet in wallets:
        send_eth(skale.web3, skale.wallet, wallet.address, TEST_ETH_AMOUNT)


def link_addresses_to_validator(skale: SkaleManager, wallets: list[Web3Wallet]) -> None:
    logger.info('Linking addresses to validator')
    for wallet in wallets:
        link_node_address(skale, wallet)


def link_node_address(skale: SkaleManager, wallet: Web3Wallet) -> None:
    validator_id = skale.validator_service.validator_id_by_address(skale.wallet.address)
    main_wallet = skale.wallet
    skale.wallet = wallet
    signature = skale.validator_service.get_link_node_signature(validator_id=validator_id)
    skale.wallet = main_wallet
    skale.validator_service.link_node_address(
        node_address=wallet.address, signature=signature, wait_for=True
    )


def init_skale_from_wallet(skale: SkaleManager, wallet: Web3Wallet) -> SkaleManager:
    return SkaleManager(skale._endpoint, skale._alias_or_address, wallet)


def register_nodes(skale_instances):
    nodes = [register_node(sk) for sk in skale_instances]
    return nodes


def register_node(skale):
    ip, public_ip, port, name = generate_random_node_data()
    port = 10000
    skale.manager.create_node(
        ip=ip,
        port=port,
        name=name,
        public_ip=public_ip,
        domain_name=DEFAULT_DOMAIN_NAME,
        wait_for=True,
    )
    node_id = skale.nodes.node_name_to_index(name)
    logger.info(f'Registered node {name}, ID: {node_id}')
    return {'node': skale.nodes.get_by_name(name), 'node_id': node_id, 'wallet': skale.wallet}


def set_up_nodes(skale, nodes_number, no_zero_id=True):
    if no_zero_id:
        nodes_number += 1
    wallets = generate_wallets(skale.web3, nodes_number)
    transfer_eth_to_wallets(skale, wallets)
    link_addresses_to_validator(skale, wallets)
    skale_instances = [init_skale_from_wallet(skale, wallet) for wallet in wallets]
    nodes_data = register_nodes(skale_instances)
    if no_zero_id:
        skale.nodes.init_exit(0)
        skale.manager.node_exit(0)
        return nodes_data[1:], skale_instances[1:]
    else:
        return nodes_data, skale_instances


def init_skale_manager(
    endpoint: str, alias_or_address: str, eth_private_key: HexStr
) -> SkaleManager:
    web3 = init_web3(endpoint)
    wallet = Web3Wallet(eth_private_key, web3)
    return SkaleManager(endpoint, alias_or_address, wallet)


def bootstrap_mirage(endpoint: str, alias_or_address: str, eth_private_key: HexStr) -> None:
    skale = init_skale_manager(endpoint, alias_or_address, eth_private_key)
    add_test_permissions(skale)
    setup_validator(skale)
    add_test2_schain_type(skale)
    add_test4_schain_type(skale)

    set_up_nodes(skale, NODES_IN_SCHAIN)
    create_schain(
        skale,
        schain_name=CHAIN_NAME,
        schain_type=2,
    )


if __name__ == '__main__':
    ENDPOINT = os.environ['ENDPOINT']
    ETH_PRIVATE_KEY = os.environ['ETH_PRIVATE_KEY']
    MANAGER_CONTRACTS = os.environ['MANAGER_CONTRACTS']
    bootstrap_mirage(ENDPOINT, MANAGER_CONTRACTS, HexStr(ETH_PRIVATE_KEY))
