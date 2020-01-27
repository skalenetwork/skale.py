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

from skale.contracts import BaseContract
from skale.transactions.tools import post_transaction
from skale.dataclasses.tx_res import TxRes
from skale.utils.constants import GAS

from skale.dataclasses.delegation_status import DelegationStatus


class DelegationService(BaseContract):
    """Wrapper for DelegationService.sol functions"""

    def register_validator(self, name: str, description: str, fee_rate: int,
                           min_delegation_amount: int) -> TxRes:
        """Registers a new validator in the SKALE Manager contracts.

        :param name: Validator name
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
        tx_hash = post_transaction(self.skale.wallet, func, GAS['register_validator'])
        return TxRes(tx_hash=tx_hash)

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
        tx_hash = post_transaction(self.skale.wallet, func, GAS['delegate'])
        return TxRes(tx_hash=tx_hash)

    def _get_delegation_ids_by_validator(self, address: str, status: DelegationStatus) -> list:
        # return self.contract.functions.getDelegationsForValidator(status.value).call({
        return self.contract.functions.getDelegationsByValidator(status.value).call({  # todo: tmp
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

    def accept_pending_delegation(self, delegation_id: int) -> TxRes:
        """Accepts a pending delegation by delegation ID.

        :param delegation_id: Delegation ID to accept
        :type delegation_id: int
        :returns: Transaction results
        :rtype: TxRes
        """
        func = self.contract.functions.acceptPendingDelegation(delegation_id)
        tx_hash = post_transaction(self.skale.wallet, func, GAS['accept_pending_delegation'])
        return TxRes(tx_hash=tx_hash)
