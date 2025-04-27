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
"""SKALE Allocator Core Escrow methods"""

import functools
from typing import Any, Callable

from eth_typing import ChecksumAddress
from web3.contract.contract import ContractFunction
from web3.types import Wei

from skale.contracts.allocator_contract import AllocatorContract
from skale.contracts.base_contract import transaction_method
from skale.transactions.result import TxRes
from skale.types.delegation import DelegationId
from skale.types.validator import ValidatorId

from skale.contracts.allocator.allocator import Allocator


def beneficiary_escrow(transaction: Callable[..., TxRes]) -> Callable[..., TxRes]:
    @functools.wraps(transaction)
    def wrapper(
        self: AllocatorContract, *args: Any, beneficiary_address: ChecksumAddress, **kwargs: Any
    ) -> TxRes:
        self.contract = self.skale.instance.get_contract('Escrow', beneficiary_address)
        return transaction(self, *args, **kwargs)

    return wrapper


class Escrow(AllocatorContract):
    @property
    @functools.lru_cache()
    def allocator(self) -> Allocator:
        return self.skale.allocator

    def init_contract(self, *args: Any) -> None:
        self.contract = self.allocator.contract

    @beneficiary_escrow
    @transaction_method
    def retrieve(self) -> 'ContractFunction':
        """Allows Holder to retrieve vested tokens from the Escrow contract

        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.retrieve()

    @beneficiary_escrow
    @transaction_method
    def retrieve_after_termination(self, address: ChecksumAddress) -> 'ContractFunction':
        """Allows Core Owner to retrieve remaining transferrable escrow balance
        after Core holder termination. Slashed tokens are non-transferable

        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.retrieveAfterTermination(address)

    @beneficiary_escrow
    @transaction_method
    def delegate(
        self, validator_id: ValidatorId, amount: Wei, delegation_period: int, info: str
    ) -> 'ContractFunction':
        """Allows Core holder to propose a delegation to a validator

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

    @beneficiary_escrow
    @transaction_method
    def request_undelegation(self, delegation_id: DelegationId) -> 'ContractFunction':
        """Allows Holder and Owner to request undelegation. Only Owner can
        request undelegation after Core holder is deactivated (upon holder termination)

        :param delegation_id: ID of the delegation
        :type delegation_id: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.requestUndelegation(delegation_id)

    @beneficiary_escrow
    @transaction_method
    def withdraw_bounty(self, validator_id: ValidatorId, to: ChecksumAddress) -> 'ContractFunction':
        """Allows Beneficiary and Vesting Owner to withdraw earned bounty.

        :param validator_id: ID of the validator
        :type validator_id: int
        :param to: Recipient address
        :type to: str
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.withdrawBounty(validator_id, to)

    @beneficiary_escrow
    @transaction_method
    def cancel_pending_delegation(self, delegation_id: DelegationId) -> 'ContractFunction':
        """Cancel pending delegation request.

        :param delegation_id: ID of the delegation to cancel
        :type delegation_id: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.cancelPendingDelegation(delegation_id)
