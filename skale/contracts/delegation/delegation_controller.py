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
from skale.utils.helper import format_fields
from skale.dataclasses.tx_res import TxRes
from skale.utils.constants import GAS
from skale.dataclasses.delegation_status import DelegationStatus


FIELDS = [
    'address', 'validator_id', 'amount', 'delegation_period', 'created',
    'started', 'finished', 'info'
]


class DelegationController(BaseContract):
    """Wrapper for DelegationController.sol functions"""

    @format_fields(FIELDS)
    def get_delegation(self, delegation_id: int) -> dict:
        """Returns delegation structure.

        :returns: Info about delegation request
        :rtype: dict
        """
        return self.__raw_get_delegation(delegation_id)

    def get_delegation_full(self, delegation_id: int) -> dict:
        """Returns delegation structure with ID and status fields.

        :returns: Info about delegation request
        :rtype: dict
        """
        delegation = self.get_delegation(delegation_id)
        delegation['id'] = delegation_id
        delegation['status'] = self._get_delegation_status(delegation_id)
        return delegation

    def __raw_get_delegation(self, delegation_id: int) -> list:
        """Returns raw delegation fields.

        :returns: Info about delegation request
        :rtype: list
        """
        return self.contract.functions.getDelegation(delegation_id).call()

    def _get_delegation_ids_by_validator(self, validator_id: int) -> list:
        delegation_ids_len = self._get_delegation_ids_len_by_validator(
            validator_id)
        return [
            self.contract.functions.delegationsByValidator(
                validator_id, _id).call()
            for _id in range(delegation_ids_len)
        ]

    def _get_delegation_ids_by_holder(self, address: str) -> list:
        delegation_ids_len = self._get_delegation_ids_len_by_holder(address)
        return [
            self.contract.functions.delegationsByHolder(address, _id).call()
            for _id in range(delegation_ids_len)
        ]

    def _get_delegation_ids_len_by_validator(self, validator_id: int) -> list:
        return self.contract.functions.getDelegationsByValidatorLength(validator_id).call()

    def _get_delegation_ids_len_by_holder(self, address: str) -> list:
        return self.contract.functions.getDelegationsByHolderLength(address).call()

    def _get_delegation_state_index(self, delegation_id: int) -> str:
        return self.contract.functions.getState(delegation_id).call()

    def _get_delegation_status(self, delegation_id: int) -> str:
        index = self._get_delegation_state_index(delegation_id)
        return DelegationStatus(index).name

    def get_all_delegations(self, delegation_ids: list) -> list:
        """Returns list of formatted delegations with particular status.

        :param delegation_ids: List of delegation IDs
        :type address: list
        :returns: List of formatted delegations
        :rtype: list
        """
        return [
            self.skale.delegation_controller.get_delegation_full(_id)
            for _id in delegation_ids
        ]

    def get_all_delegations_by_holder(self, address: str) -> list:
        """Returns list of formatted delegations for token holder.

        :param address: Ethereum address
        :type address: str
        :returns: List of formatted delegation requests
        :rtype: list
        """
        delegation_ids = self._get_delegation_ids_by_holder(address)
        return self.get_all_delegations(delegation_ids)

    def get_all_delegations_by_validator(self, validator_id: int) -> list:
        """Returns list of formatted delegations for validator.

        :param validator_id: ID of the validator
        :type address: int
        :returns: List of formatted delegations
        :rtype: list
        """
        validator_id = int(validator_id)
        delegation_ids = self._get_delegation_ids_by_validator(validator_id)
        return self.get_all_delegations(delegation_ids)

    @transaction_method(gas_limit=GAS['delegate'])
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
        return self.contract.functions.delegate(validator_id, amount, delegation_period, info)

    @transaction_method(gas_limit=GAS['accept_pending_delegation'])
    def accept_pending_delegation(self, delegation_id: int) -> TxRes:
        """Accepts a pending delegation by delegation ID.

        :param delegation_id: Delegation ID to accept
        :type delegation_id: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.acceptPendingDelegation(delegation_id)

    @transaction_method(gas_limit=GAS['cancel_pending_delegation'])
    def cancel_pending_delegation(self, delegation_id: int) -> TxRes:
        """Cancel pending delegation request.

        :param delegation_id: ID of the delegation to cancel
        :type delegation_id: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.cancelPendingDelegation(delegation_id)

    @transaction_method(gas_limit=GAS['request_undelegation'])
    def request_undelegation(self, delegation_id: int) -> TxRes:
        """ This method is  for undelegating request in the end of
            delegation period (3/6/12 months)

        :param delegation_id: ID of the delegation to undelegate
        :type delegation_id: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.requestUndelegation(delegation_id)

    def get_delegated_to_validator_now(self, validator_id: int) -> int:
        """Amount of delegated tokens to the validator

        :param validator_id: ID of the validator
        :type validator_id: int
        :returns: Amount of delegated tokens
        :rtype: int
        """
        return self.contract.functions.getAndUpdateDelegatedToValidatorNow(validator_id).call()

    def get_delegated_amount(self, address: str) -> int:
        """Amount of delegated tokens by token holder

        :param address: Token holder address
        :type address: str
        :returns: Amount of delegated tokens
        :rtype: int
        """
        return self.contract.functions.getAndUpdateDelegatedAmount(address).call()
