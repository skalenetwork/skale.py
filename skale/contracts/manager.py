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
""" SKALE manager operations """


import logging
import socket


import skale.utils.helper as Helper
from skale.contracts import BaseContract
from skale.utils.constants import GAS, NODE_DEPOSIT, OP_TYPES
from skale.utils.helper import sign_and_send

logger = logging.getLogger(__name__)


class Manager(BaseContract):
    def create_node(self, ip, port, name, wallet, public_ip=None):
        logger.info(
            f'create_node: {ip}:{port}, public ip: {public_ip} name: {name}')

        token = self.skale.get_contract_by_name('token')
        skale_nonce = Helper.generate_nonce()
        pk = Helper.private_key_to_public(wallet['private_key'])

        if not public_ip:
            public_ip = ip

        transaction_data = self.create_node_data_to_bytes(
            ip, public_ip, port, name, pk, skale_nonce)

        op = token.contract.functions.transfer(self.address, NODE_DEPOSIT,
                                               transaction_data)
        tx = sign_and_send(self.skale, op, GAS['create_node'], wallet)
        return {'tx': tx, 'nonce': skale_nonce}

    def create_node_data_to_bytes(self, ip, public_ip, port, name, pk, nonce):
        pk_fix = str(pk)[2:]

        type_bytes = OP_TYPES['create_node'].to_bytes(1, byteorder='big')
        port_bytes = port.to_bytes(2, byteorder='big')
        nonce_bytes = nonce.to_bytes(2, byteorder='big')  # todo
        ip_bytes = socket.inet_aton(ip)
        public_ip_bytes = socket.inet_aton(public_ip)
        pk_bytes = bytes.fromhex(pk_fix)
        name_bytes = name.encode()

        data_bytes = (
            type_bytes +
            port_bytes +
            nonce_bytes +
            ip_bytes +
            public_ip_bytes +
            pk_bytes +
            name_bytes
        )
        logger.info(
            f'create_node_data_to_bytes bytes: {self.skale.web3.toHex(data_bytes)}'
        )

        return data_bytes

    def create_schain(self, lifetime, type_of_nodes, deposit, name, wallet):
        logger.info(
            f'create_schain: type_of_nodes: {type_of_nodes}, name: {name}')

        token = self.skale.get_contract_by_name('token')
        skale_nonce = Helper.generate_nonce()
        transaction_data = self.create_schain_data_to_bytes(
            lifetime, type_of_nodes, name, skale_nonce)

        op = token.contract.functions.transfer(self.address, deposit,
                                               transaction_data)
        tx = sign_and_send(self.skale, op, GAS['create_node'], wallet)
        return {'tx': tx, 'nonce': skale_nonce}

    def create_schain_data_to_bytes(self, lifetime, type_of_nodes, name,
                                    nonce):
        type_bytes = OP_TYPES['create_schain'].to_bytes(1, byteorder='big')

        lifetime_hex = lifetime.to_bytes(32, byteorder='big')
        type_of_nodes_hex = type_of_nodes.to_bytes(1, byteorder='big')
        nonce_hex = nonce.to_bytes(2, byteorder='big')
        name_hex = name.encode()

        data_bytes = type_bytes + lifetime_hex + type_of_nodes_hex + nonce_hex + name_hex
        logger.info(
            f'create_schain_data_to_bytes bytes: {self.skale.web3.toHex(data_bytes)}'
        )
        return data_bytes

    def get_bounty(self, node_id, wallet):
        op = self.contract.functions.getBounty(node_id)
        tx = sign_and_send(self.skale, op, GAS['get_bounty'], wallet)
        return {'tx': tx}

    def send_verdict(self, validator, node_id, downtime, latency, wallet):
        op = self.contract.functions.sendVerdict(validator, node_id, downtime,
                                                 latency)
        tx = sign_and_send(self.skale, op, GAS['send_verdict'], wallet)
        return {'tx': tx}
