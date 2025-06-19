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

from typing import Any, Dict, List

from eth_typing import ChecksumAddress
from web3.contract.contract import ContractFunction
from web3.types import Wei

from skale.contracts.base_contract import transaction_method
from skale.contracts.skale_manager_contract import SkaleManagerContract
from skale.types.delegation import Delegation, DelegationId, DelegationStatus, FullDelegation
from skale.types.validator import ValidatorId
from skale.utils.helper import format_fields


FIELDS = [
    'address',
    'validator_id',
    'amount',
    'delegation_period',
    'created',
    'started',
    'finished',
    'info',
]


class DelegationController(SkaleManagerContract):
    """Wrapper for DelegationController.sol functions"""

    @format_fields(FIELDS)
    def get_untyped_delegation(self, delegation_id: DelegationId) -> List[Any]:
        """Returns delegation structure.

        :returns: Info about delegation request
        :rtype: list
        """
        return self.__raw_get_delegation(delegation_id)

    def get_delegation(self, delegation_id: DelegationId) -> Delegation:
        delegation = self.get_untyped_delegation(delegation_id)
        if delegation is None:
            raise ValueError("Can't get delegation with id ", delegation_id)
        if isinstance(delegation, dict):
            return self._to_delegation(delegation)
        if isinstance(delegation, list):
            return self._to_delegation(delegation[0])
        raise TypeError(delegation_id)

    def get_delegation_full(self, delegation_id: DelegationId) -> FullDelegation:
        """Returns delegation structure with ID and status fields.

        :returns: Info about delegation request
        :rtype: dict
        """
        delegation = self.get_delegation(delegation_id)
        return FullDelegation(
            {
                'id': delegation_id,
                'status': self._get_delegation_status(delegation_id),
                **delegation,
            }
        )

    def __raw_get_delegation(self, delegation_id: DelegationId) -> List[Any]:
        """Returns raw delegation fields.

        :returns: Info about delegation request
        :rtype: list
        """
        return list(self.contract.functions.getDelegation(delegation_id).call())

    def _get_delegation_ids_by_validator(self, validator_id: ValidatorId) -> List[DelegationId]:
        delegation_ids_len = self._get_delegation_ids_len_by_validator(validator_id)
        return [
            DelegationId(self.contract.functions.delegationsByValidator(validator_id, _id).call())
            for _id in range(delegation_ids_len)
        ]

    def _get_delegation_ids_by_holder(self, address: ChecksumAddress) -> List[DelegationId]:
        delegation_ids_len = self._get_delegation_ids_len_by_holder(address)
        return [
            DelegationId(self.contract.functions.delegationsByHolder(address, _id).call())
            for _id in range(delegation_ids_len)
        ]

    def _get_delegation_ids_len_by_validator(self, validator_id: ValidatorId) -> int:
        return int(self.contract.functions.getDelegationsByValidatorLength(validator_id).call())

    def _get_delegation_ids_len_by_holder(self, address: ChecksumAddress) -> int:
        return int(self.contract.functions.getDelegationsByHolderLength(address).call())

    def _get_delegation_state_index(self, delegation_id: DelegationId) -> int:
        return int(self.contract.functions.getState(delegation_id).call())

    def _get_delegation_status(self, delegation_id: DelegationId) -> DelegationStatus:
        index = self._get_delegation_state_index(delegation_id)
        return DelegationStatus(index)

    def get_all_delegations(self, delegation_ids: List[DelegationId]) -> List[FullDelegation]:
        """Returns list of formatted delegations with particular status.

        :param delegation_ids: List of delegation IDs
        :type address: list
        :returns: List of formatted delegations
        :rtype: list
        """
        return [self.skale.delegation_controller.get_delegation_full(_id) for _id in delegation_ids]

    def get_all_delegations_by_holder(self, address: ChecksumAddress) -> List[FullDelegation]:
        """Returns list of formatted delegations for token holder.

        :param address: Ethereum address
        :type address: ChecksumAddress
        :returns: List of formatted delegation requests
        :rtype: list
        """
        delegation_ids = self._get_delegation_ids_by_holder(address)
        return self.get_all_delegations(delegation_ids)

    def get_all_delegations_by_validator(self, validator_id: ValidatorId) -> List[FullDelegation]:
        """Returns list of formatted delegations for validator.

        :param validator_id: ID of the validator
        :type validator_id: ValidatorId
        :returns: List of formatted delegations
        :rtype: list
        """
        delegation_ids = self._get_delegation_ids_by_validator(validator_id)
        return self.get_all_delegations(delegation_ids)

    @transaction_method
    def delegate(
        self, validator_id: ValidatorId, amount: Wei, delegation_period: int, info: str
    ) -> 'ContractFunction':
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

    @transaction_method
    def accept_pending_delegation(self, delegation_id: DelegationId) -> 'ContractFunction':
        """Accepts a pending delegation by delegation ID.

        :param delegation_id: Delegation ID to accept
        :type delegation_id: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.acceptPendingDelegation(delegation_id)

    @transaction_method
    def cancel_pending_delegation(self, delegation_id: DelegationId) -> 'ContractFunction':
        """Cancel pending delegation request.

        :param delegation_id: ID of the delegation to cancel
        :type delegation_id: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.cancelPendingDelegation(delegation_id)

    @transaction_method
    def request_undelegation(self, delegation_id: DelegationId) -> 'ContractFunction':
        """This method is  for undelegating request in the end of
            delegation period (3/6/12 months)

        :param delegation_id: ID of the delegation to undelegate
        :type delegation_id: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.requestUndelegation(delegation_id)

    def get_delegated_to_validator_now(self, validator_id: ValidatorId) -> Wei:
        """Amount of delegated tokens to the validator

        :param validator_id: ID of the validator
        :type validator_id: int
        :returns: Amount of delegated tokens
        :rtype: int
        """
        return Wei(self.contract.functions.getAndUpdateDelegatedToValidatorNow(validator_id).call())

    def get_delegated_to_validator(self, validator_id: ValidatorId, month: int) -> Wei:
        """Amount of delegated tokens to the validator unil month

        :param validator_id: ID of the validator
        :type validator_id: int
        :param month: last requested month
        :type month: int
        :returns: Amount of delegated tokens
        :rtype: int
        """

        return Wei(self.contract.functions.getDelegatedToValidator(validator_id, month).call())

    def get_delegated_amount(self, address: ChecksumAddress) -> Wei:
        """Amount of delegated tokens by token holder

        :param address: Token holder address
        :type address: ChecksumAddress
        :returns: Amount of delegated tokens
        :rtype: int
        """
        return Wei(self.contract.functions.getAndUpdateDelegatedAmount(address).call())

    def _to_delegation(self, delegation: Dict[str, Any]) -> Delegation:
        return Delegation(
            {
                'address': ChecksumAddress(delegation['address']),
                'validator_id': ValidatorId(delegation['validator_id']),
                'amount': Wei(delegation['amount']),
                'delegation_period': int(delegation['delegation_period']),
                'created': int(delegation['created']),
                'started': int(delegation['started']),
                'finished': int(delegation['finished']),
                'info': str(delegation['info']),
            }
        )
