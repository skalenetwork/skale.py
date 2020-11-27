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
""" SKALE manager operations """


import logging
import socket

from eth_abi import encode_abi

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.utils import helper
from skale.transactions.result import TxRes

logger = logging.getLogger(__name__)


class Manager(BaseContract):

    @transaction_method
    def create_node(self, ip, port, name, public_ip=None):
        logger.info(
            f'create_node: {ip}:{port}, public ip: {public_ip} name: {name}')
        skale_nonce = helper.generate_nonce()
        if not public_ip:
            public_ip = ip
        ip_bytes = socket.inet_aton(ip)
        public_ip_bytes = socket.inet_aton(public_ip)
        pk_parts_bytes = helper.split_public_key(self.skale.wallet.public_key)
        return self.contract.functions.createNode(
            port,
            skale_nonce,
            ip_bytes,
            public_ip_bytes,
            pk_parts_bytes,
            name
        )

    def create_default_schain(self, name):
        lifetime = 3600
        nodes_type = 4
        price_in_wei = self.skale.schains.get_schain_price(
            nodes_type, lifetime)
        return self.create_schain(lifetime, nodes_type, price_in_wei, name,
                                  wait_for=True)

    @transaction_method
    def create_schain(self, lifetime, type_of_nodes, deposit, name):
        logger.info(
            f'create_schain: type_of_nodes: {type_of_nodes}, name: {name}')

        token = self.skale.get_contract_by_name('token')
        skale_nonce = helper.generate_nonce()
        tx_data = encode_abi(
            ['uint', 'uint8', 'uint16', 'string'],
            [lifetime, type_of_nodes, skale_nonce, name]
        )
        return token.contract.functions.send(self.address, deposit, tx_data)

    @transaction_method
    def get_bounty(self, node_id):
        return self.contract.functions.getBounty(node_id)

    @transaction_method
    def delete_schain(self, schain_name):
        return self.contract.functions.deleteSchain(schain_name)

    @transaction_method
    def node_exit(self, node_id):
        return self.contract.functions.nodeExit(node_id)

    @transaction_method
    def grant_role(self, role: bytes, address: str) -> TxRes:
        return self.contract.functions.grantRole(role, address)

    def default_admin_role(self) -> bytes:
        return self.contract.functions.DEFAULT_ADMIN_ROLE().call()

    def admin_role(self) -> bytes:
        return self.contract.functions.ADMIN_ROLE().call()

    def has_role(self, role: bytes, address: str) -> bool:
        return self.contract.functions.hasRole(role, address).call()
