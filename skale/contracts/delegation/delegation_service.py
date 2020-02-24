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

from skale.dataclasses.delegation_status import DelegationStatus


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
    def delegate(self, validator_id: int, amount: int, delegation_period: int, info: str) -> TxRes:
        """Creates request to delegate amount of tokens to validator_id.

        :param validator_id: ID of the validator to delegate tokens
        :type validator_id: int
        :param amount: Amount of tokens to delegate
        :type amount: int
        :param delegation_period: Period of delegation
        :type delegation_period: int
        :param info: Delegation request information
        :type info: str
        :returns: Transaction results
        :rtype: TxRes
        """
        func = self.contract.functions.delegate(validator_id, amount, delegation_period, info)
        return post_transaction(self.skale.wallet, func, GAS['delegate'])

    def _get_delegation_ids_by_validator(self, address: str, status: DelegationStatus) -> list:
        # return self.contract.functions.getDelegationsByValidator(status.value).call({  # todo: tmp
        return self.contract.functions.getDelegationsForValidator(status.value).call({
            'from': address
        })

    def _get_delegation_ids_by_holder(self, address: str, status: DelegationStatus) -> list:
        return self.contract.functions.getDelegationsByHolder(status.value).call({
            'from': address
        })

    def get_delegations(self, address: str, status: DelegationStatus, account_type: str) -> list:
        """Returns list of formatted delegations with particular status.

        :param address: Ethereum address
        :type address: str
        :param status: Delegation status
        :type address: DelegationStatus
        :param address: Account type - holder or validator
        :type address: str
        :returns: List of formatted delegation requests
        :rtype: list
        """
        delegations = []

        if account_type == 'validator':
            delegation_ids = self._get_delegation_ids_by_validator(address, status)
        else:
            delegation_ids = self._get_delegation_ids_by_holder(address, status)

        for _id in delegation_ids:
            delegation = self.skale.delegation_controller.get_delegation(_id)
            delegation['status'] = status.name
            delegation['id'] = _id
            delegations.append(delegation)
        return delegations

    def get_all_delegations(self, address: str, account_type: str):
        """Returns list of formatted delegations.

        :param address: Ethereum address
        :type address: str
        :param address: Account type - holder or validator
        :type address: str
        :returns: List of formatted delegation requests
        :rtype: list
        """
        delegations = []
        for status in DelegationStatus:
            _delegations = self.get_delegations(address, status, account_type)
            delegations.extend(_delegations)
        return delegations

    def get_all_delegations_by_holder(self, address: str) -> list:
        """Returns list of formatted delegations for token holder.

        :param address: Ethereum address
        :type address: str
        :returns: List of formatted delegation requests
        :rtype: list
        """
        return self.get_all_delegations(address, 'holder')

    def get_all_delegations_by_validator(self, address: str) -> list:
        """Returns list of formatted delegations for validator.

        :param address: Ethereum address
        :type address: str
        :returns: List of formatted delegation requests
        :rtype: list
        """
        return self.get_all_delegations(address, 'validator')

    @transaction_method
    def accept_pending_delegation(self, delegation_id: int) -> TxRes:
        """Accepts a pending delegation by delegation ID.

        :param delegation_id: Delegation ID to accept
        :type delegation_id: int
        :returns: Transaction results
        :rtype: TxRes
        """
        func = self.contract.functions.acceptPendingDelegation(delegation_id)
        return post_transaction(self.skale.wallet, func, GAS['accept_pending_delegation'])

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

    @transaction_method
    def cancel_pending_delegation(self, delegation_id: int) -> TxRes:
        """Cancel pending delegation request.

        :param delegation_id: ID of the delegation to cancel
        :type delegation_id: int
        :returns: Transaction results
        :rtype: TxRes
        """
        func = self.contract.functions.cancelPendingDelegation(delegation_id)
        return post_transaction(self.skale.wallet, func, GAS['cancel_pending_delegation'])

    def get_delegated_amount(self, validator_id: int) -> int:
        return self.contract.functions.getDelegatedAmount(validator_id).call()

    def get_delegated_of(self, address: str) -> int:
        return self.contract.functions.getDelegatedOf(address).call()

    @transaction_method
    def withdraw_bounty(self, bounty_collection_address: str, amount: int) -> TxRes:
        """Withdraw earned validator bounty.

        :param bounty_collection_address: Address to transfer funds
        :type bounty_collection_address: str
        :param amount: Amount of tokens to withdraw
        :type amount: int
        :returns: Transaction results
        :rtype: TxRes
        """
        func = self.contract.functions.withdrawBounty(bounty_collection_address, amount)
        return post_transaction(self.skale.wallet, func, GAS['withdraw_bounty'])

    def get_earned_bounty_amount(self, address: str) -> int:
        """Returns earned bounty amount for validator.

        :param address: Ethereum address
        :type address: str
        :returns: Amount of earned bounty
        :rtype: int
        """
        return self.contract.functions.getEarnedBountyAmount().call({
            'from': address
        })
