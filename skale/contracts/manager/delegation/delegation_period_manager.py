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

from eth_typing import ChecksumAddress
from web3.contract.contract import ContractFunction

from skale.contracts.base_contract import transaction_method
from skale.contracts.skale_manager_contract import SkaleManagerContract


class DelegationPeriodManager(SkaleManagerContract):
    """Wrapper for DelegationPeriodManager.sol functions"""

    @transaction_method
    def set_delegation_period(self, months_count: int, stake_multiplier: int) -> 'ContractFunction':
        return self.contract.functions.setDelegationPeriod(
            monthsCount=months_count, stakeMultiplier=stake_multiplier
        )

    def is_delegation_period_allowed(self, months_count: int) -> bool:
        return bool(
            self.contract.functions.isDelegationPeriodAllowed(monthsCount=months_count).call()
        )

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> 'ContractFunction':
        return self.contract.functions.grantRole(role, address)

    def delegation_period_setter_role(self) -> bytes:
        return bytes(self.contract.functions.DELEGATION_PERIOD_SETTER_ROLE().call())

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.hasRole(role, address).call())
