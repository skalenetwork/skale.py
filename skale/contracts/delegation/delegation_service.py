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

from skale.contracts import BaseContract, transaction_method
from skale.transactions.tools import post_transaction
from skale.dataclasses.tx_res import TxRes
from skale.utils.constants import GAS


class DelegationService(BaseContract):
    """Wrapper for DelegationService.sol functions"""

    @transaction_method
    def register_validator(self, name: str, description: str, fee_rate: int,
                           min_delegation_amount: int) -> TxRes:
        """Registers a new validator in the SKALE Manager contracts.

        :param name:z Validator name
        :type name: str
        :param description: Validator description
        :type description: str
        :param fee_rate: Validator fee rate
        :type fee_rate: int
        :param min_delegation_amount: Minimal delegation amount
        :type min_delegation_amount: int
        :returns: Transaction results
        :rtype: TxRes
        """
        func = self.contract.functions.registerValidator(
            name, description, fee_rate, min_delegation_amount)
        return post_transaction(self.skale.wallet, func, GAS['register_validator'])

    @transaction_method
    def link_node_address(self, node_address: str) -> TxRes:
        """Link node address to your validator account.

        :param node_address: Address of the node to link
        :type node_address: str
        :returns: Transaction results
        :rtype: TxRes
        """
        func = self.contract.functions.linkNodeAddress(node_address)
        return post_transaction(self.skale.wallet, func, GAS['link_node_address'])

    @transaction_method
    def unlink_node_address(self, node_address: str) -> TxRes:
        """Unlink node address from your validator account.

        :param node_address: Address of the node to unlink
        :type node_address: str
        :returns: Transaction results
        :rtype: TxRes
        """
        func = self.contract.functions.unlinkNodeAddress(node_address)
        return post_transaction(self.skale.wallet, func, GAS['unlink_node_address'])
