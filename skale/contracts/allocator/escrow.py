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
""" SKALE Allocator Core Escrow methods """

import functools

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes


def beneficiary_escrow(transaction):
    @functools.wraps(transaction)
    def wrapper(self, *args, beneficiary_address, **kwargs):
        self.contract = self.init_beneficiary_contract(beneficiary_address)
        return transaction(self, *args, **kwargs)
    return wrapper


class Escrow(BaseContract):
    @property
    @functools.lru_cache()
    def allocator(self):
        return self.skale.get_contract_by_name('allocator')

    def init_beneficiary_contract(self, beneficiary_address: str):
        beneficiary_escrow_address = self.allocator.get_escrow_address(beneficiary_address)
        return Escrow(self.skale, f'escrow_{beneficiary_address}', beneficiary_escrow_address,
                      self.contract.abi).contract

    @beneficiary_escrow
    @transaction_method
    def retrieve(self) -> TxRes:
        """Allows Holder to retrieve vested tokens from the Escrow contract

        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.retrieve()

    @beneficiary_escrow
    @transaction_method
    def retrieve_after_termination(self, address: str) -> TxRes:
        """Allows Core Owner to retrieve remaining transferrable escrow balance
        after Core holder termination. Slashed tokens are non-transferable

        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.retrieveAfterTermination(address)

    @beneficiary_escrow
    @transaction_method
    def delegate(self, validator_id: int, amount: int, delegation_period: int, info: str) -> TxRes:
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
    def request_undelegation(self, delegation_id: int) -> TxRes:
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
    def withdraw_bounty(self, validator_id: int, to: str) -> TxRes:
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
    def cancel_pending_delegation(self, delegation_id: int) -> TxRes:
        """Cancel pending delegation request.

        :param delegation_id: ID of the delegation to cancel
        :type delegation_id: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.cancelPendingDelegation(delegation_id)
