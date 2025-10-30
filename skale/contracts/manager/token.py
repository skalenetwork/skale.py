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
"""SKALE token operations"""

from eth_typing import ChecksumAddress
from web3.contract.contract import ContractFunction
from web3.types import Wei

from skale.contracts.base_contract import transaction_method
from skale.contracts.skale_manager_contract import SkaleManagerContract


class Token(SkaleManagerContract):
    @transaction_method
    def transfer(self, address: ChecksumAddress, value: Wei) -> 'ContractFunction':
        return self.contract.functions.send(address, value, b'')

    def get_balance(self, address: ChecksumAddress) -> Wei:
        return Wei(self.contract.functions.balanceOf(address).call())

    @transaction_method
    def add_authorized(self, address: ChecksumAddress) -> 'ContractFunction':  # pragma: no cover
        return self.contract.functions.addAuthorized(address)

    def get_and_update_slashed_amount(self, address: ChecksumAddress) -> Wei:
        return Wei(self.contract.functions.getAndUpdateSlashedAmount(address).call())

    @transaction_method
    def mint(
        self,
        address: ChecksumAddress,
        amount: Wei,
        user_data: bytes = b'',
        operator_data: bytes = b'',
    ) -> 'ContractFunction':
        return self.contract.functions.mint(address, amount, user_data, operator_data)
