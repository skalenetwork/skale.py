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


from skale.contracts import BaseContract, transaction_method
from skale.transactions.tools import post_transaction
from skale.utils import helper
from skale.utils.constants import GAS, NODE_DEPOSIT, OP_TYPES

logger = logging.getLogger(__name__)


class Manager(BaseContract):
    @transaction_method
    def create_node(self, ip, port, name, public_ip=None):
        logger.info(
            f'create_node: {ip}:{port}, public ip: {public_ip} name: {name}')

        token = self.skale.get_contract_by_name('token')
        skale_nonce = helper.generate_nonce()
        pk = self.skale.wallet.public_key

        if not public_ip:
            public_ip = ip

        transaction_data = self.create_node_data_to_bytes(
            ip, public_ip, port, name, pk, skale_nonce)

        op = token.contract.functions.send(self.address, NODE_DEPOSIT,
                                           transaction_data)
        tx = post_transaction(self.skale.wallet, op, GAS['create_node'])
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
            type_bytes
            + port_bytes  # noqa: W503
            + nonce_bytes  # noqa: W503
            + ip_bytes  # noqa: W503
            + public_ip_bytes  # noqa: W503
            + pk_bytes  # noqa: W503
            + name_bytes  # noqa: W503
        )
        logger.info(
            f'create_node_data_to_bytes bytes: {self.skale.web3.toHex(data_bytes)}'
        )

        return data_bytes

    def create_default_schain(self, name):
        lifetime = 3600
        nodes_type = 4
        price_in_wei = self.skale.schains.get_schain_price(nodes_type, lifetime)
        return self.create_schain(lifetime, nodes_type, price_in_wei, name,
                                  wait_for=True)

    @transaction_method
    def create_schain(self, lifetime, type_of_nodes, deposit, name):
        logger.info(
            f'create_schain: type_of_nodes: {type_of_nodes}, name: {name}')

        token = self.skale.get_contract_by_name('token')
        skale_nonce = helper.generate_nonce()
        transaction_data = self.create_schain_data_to_bytes(
            lifetime, type_of_nodes, name, skale_nonce)

        op = token.contract.functions.send(self.address, deposit,
                                           transaction_data)
        tx = post_transaction(self.skale.wallet, op, GAS['create_schain'])
        return {'tx': tx, 'nonce': skale_nonce}

    def create_schain_data_to_bytes(self, lifetime, type_of_nodes, name,
                                    nonce):
        type_bytes = OP_TYPES['create_schain'].to_bytes(1, byteorder='big')

        lifetime_hex = lifetime.to_bytes(32, byteorder='big')
        type_of_nodes_hex = type_of_nodes.to_bytes(1, byteorder='big')
        nonce_hex = nonce.to_bytes(2, byteorder='big')
        name_hex = name.encode()

        data_bytes = (type_bytes + lifetime_hex +
                      type_of_nodes_hex + nonce_hex + name_hex)
        logger.info(
            f'create_schain_data_to_bytes bytes:'
            f'{self.skale.web3.toHex(data_bytes)}'
        )
        return data_bytes

    @transaction_method
    def get_bounty(self, node_id):
        op = self.contract.functions.getBounty(node_id)
        tx = post_transaction(self.skale.wallet, op, GAS['get_bounty'])
        return {'tx': tx}

    @transaction_method
    def send_verdict(self, validator, node_id, downtime, latency):
        op = self.contract.functions.sendVerdict(validator, node_id, downtime,
                                                 latency)
        tx = post_transaction(self.skale.wallet, op, GAS['send_verdict'])
        return {'tx': tx}

    @transaction_method
    def send_verdicts(self, validator, nodes_ids, downtimes, latencies):
        op = self.contract.functions.sendVerdicts(validator, nodes_ids,
                                                  downtimes, latencies)
        tx = post_transaction(self.skale.wallet, op, GAS['send_verdicts'])
        return {'tx': tx}

    @transaction_method
    def deregister(self, node_id):
        op = self.contract.functions.deleteNode(node_id)
        tx = post_transaction(self.skale.wallet, op, GAS['delete_node'])
        return {'tx': tx}

    @transaction_method
    def delete_schain(self, schain_name):
        op = self.contract.functions.deleteSchain(schain_name)
        tx = post_transaction(self.skale.wallet, op, GAS['delete_schain'])
        return {'tx': tx}

    @transaction_method
    def delete_node_by_root(self, node_id):
        op = self.contract.functions.deleteNodeByRoot(node_id)
        tx = post_transaction(self.skale.wallet, op, GAS['delete_node_by_root'])
        return {'tx': tx}
