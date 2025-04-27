#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019-Present SKALE Labs
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
"""SKALE manager operations"""

import logging
import socket

from eth_abi.abi import encode
from eth_typing import ChecksumAddress
from web3.contract.contract import ContractFunction

from skale.contracts.base_contract import transaction_method
from skale.contracts.skale_manager_contract import SkaleManagerContract
from skale.types.node import NodeId, Port
from skale.types.schain import SchainName
from skale.utils import helper
from skale.transactions.result import TxRes
from skale.dataclasses.schain_options import SchainOptions, get_default_schain_options

logger = logging.getLogger(__name__)


class Manager(SkaleManagerContract):
    @transaction_method
    def create_node(
        self, ip: str, port: Port, name: str, domain_name: str, public_ip: str | None = None
    ) -> 'ContractFunction':
        logger.info(f'create_node: {ip}:{port}, name: {name}, domain_name: {domain_name}')
        skale_nonce = helper.generate_nonce()
        if not public_ip:
            public_ip = ip
        ip_bytes = socket.inet_aton(ip)
        public_ip_bytes = socket.inet_aton(public_ip)
        pk_parts_bytes = helper.split_public_key(self.skale.wallet.public_key)
        return self.contract.functions.createNode(
            port, skale_nonce, ip_bytes, public_ip_bytes, pk_parts_bytes, name, domain_name
        )

    def create_default_schain(self, name: SchainName) -> TxRes:
        lifetime = 3600
        nodes_type = self.skale.schains_internal.number_of_schain_types()
        price_in_wei = self.skale.schains.get_schain_price(nodes_type, lifetime)
        return self.create_schain(lifetime, nodes_type, price_in_wei, name, wait_for=True)

    @transaction_method
    def create_schain(
        self,
        lifetime: int,
        type_of_nodes: int,
        deposit: str,
        name: SchainName,
        schain_originator: ChecksumAddress | None = None,
        options: SchainOptions | None = None,
    ) -> 'ContractFunction':
        logger.info(f'create_schain: type_of_nodes: {type_of_nodes}, name: {name}')
        skale_nonce = helper.generate_nonce()

        if schain_originator is None:
            schain_originator = self.skale.wallet.address
        if not options:
            options = get_default_schain_options()

        tx_data = encode(
            ['(uint,uint8,uint16,string,address,(string,bytes)[])'],
            [(lifetime, type_of_nodes, skale_nonce, name, schain_originator, options.to_tuples())],
        )

        return self.skale.token.contract.functions.send(self.address, deposit, tx_data)

    @transaction_method
    def get_bounty(self, node_id: NodeId) -> 'ContractFunction':
        return self.contract.functions.getBounty(node_id)

    @transaction_method
    def delete_schain(self, schain_name: SchainName) -> 'ContractFunction':
        return self.contract.functions.deleteSchain(schain_name)

    @transaction_method
    def delete_schain_by_root(self, schain_name: SchainName) -> 'ContractFunction':
        return self.contract.functions.deleteSchainByRoot(schain_name)

    @transaction_method
    def node_exit(self, node_id: NodeId) -> 'ContractFunction':
        return self.contract.functions.nodeExit(node_id)

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> 'ContractFunction':
        return self.contract.functions.grantRole(role, address)

    def default_admin_role(self) -> bytes:
        return bytes(self.contract.functions.DEFAULT_ADMIN_ROLE().call())

    def admin_role(self) -> bytes:
        return bytes(self.contract.functions.ADMIN_ROLE().call())

    def schain_removal_role(self) -> bytes:
        return bytes(self.contract.functions.SCHAIN_REMOVAL_ROLE().call())

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.hasRole(role, address).call())
