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

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes
from skale.utils.constants import ALLOCATOR_GAS


class CoreEscrow(BaseContract):
    @transaction_method(gas_limit=ALLOCATOR_GAS['retrieve'])
    def retrieve(self) -> TxRes:
        """Allows Holder to retrieve vested tokens from the Escrow contract

        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.retrieve()

    @transaction_method(gas_limit=ALLOCATOR_GAS['retrieve_after_termination'])
    def retrieve_after_termination(self) -> TxRes:
        """Allows Core Owner to retrieve remaining transferrable escrow balance
        after Core holder termination. Slashed tokens are non-transferable

        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.retrieveAfterTermination()

    @transaction_method(gas_limit=ALLOCATOR_GAS['delegate'])
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

    @transaction_method(gas_limit=ALLOCATOR_GAS['request_undelegation'])
    def request_undelegation(self, delegation_id: int) -> TxRes:
        """Allows Holder and Owner to request undelegation. Only Owner can
        request undelegation after Core holder is deactivated (upon holder termination)

        :param delegation_id: ID of the delegation
        :type delegation_id: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.requestUndelegation(delegation_id)
