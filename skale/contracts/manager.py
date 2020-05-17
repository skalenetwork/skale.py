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

from skale.contracts import BaseContract, transaction_method
from skale.utils import helper
from skale.utils.constants import GAS

logger = logging.getLogger(__name__)


class Manager(BaseContract):

    @transaction_method(gas_limit=GAS['create_node'])
    def create_node(self, ip, port, name, public_ip=None):
        logger.info(
            f'create_node: {ip}:{port}, public ip: {public_ip} name: {name}')
        skale_nonce = helper.generate_nonce()
        if not public_ip:
            public_ip = ip
        pk = self.skale.wallet.public_key

        ip_bytes = socket.inet_aton(ip)
        public_ip_bytes = socket.inet_aton(public_ip)
        # pk to bytes without 0x
        pk_bytes = bytes.fromhex(str(pk)[2:])

        return self.contract.functions.createNode(
            port,
            skale_nonce,
            ip_bytes,
            public_ip_bytes,
            pk_bytes,
            name
        )

    def create_default_schain(self, name):
        lifetime = 3600
        nodes_type = 4
        price_in_wei = self.skale.schains.get_schain_price(
            nodes_type, lifetime)
        return self.create_schain(lifetime, nodes_type, price_in_wei, name,
                                  wait_for=True)

    @transaction_method(gas_limit=GAS['create_schain'])
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

    @transaction_method(gas_limit=GAS['get_bounty'])
    def get_bounty(self, node_id):
        return self.contract.functions.getBounty(node_id)

    @transaction_method(gas_limit=GAS['send_verdict'])
    def send_verdict(self, validator, verdict_data):
        return self.contract.functions.sendVerdict(
            validator,
            verdict_data
        )

    @transaction_method(gas_limit=GAS['send_verdicts'])
    def send_verdicts(self, validator, verdicts_data):
        return self.contract.functions.sendVerdicts(
            validator,
            verdicts_data
        )

    @transaction_method(gas_limit=GAS['delete_node'])
    def deregister(self, node_id):
        return self.contract.functions.deleteNode(node_id)

    @transaction_method(gas_limit=GAS['delete_schain'])
    def delete_schain(self, schain_name):
        return self.contract.functions.deleteSchain(schain_name)

    @transaction_method(gas_limit=GAS['delete_node_by_root'])
    def delete_node_by_root(self, node_id):
        return self.contract.functions.deleteNodeByRoot(node_id)

    @transaction_method(gas_limit=GAS['node_exit'])
    def node_exit(self, node_id):
        return self.contract.functions.nodeExit(node_id)
