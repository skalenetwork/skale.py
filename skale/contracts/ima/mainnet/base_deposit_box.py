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
from skale.contracts.skale_contract import SkaleContract
from skale.types.schain import SchainName


class BaseDepositBox(SkaleContract):
    def is_whitelisted(self, schain_name: SchainName) -> bool:
        return self.contract.functions.isWhitelisted(schain_name).call()

    @transaction_method
    def enable_whitelist(self, schain_name: SchainName) -> ContractFunction:
        return self.contract.functions.enableWhitelist(schain_name)

    @transaction_method
    def disable_whitelist(self, schain_name: SchainName) -> ContractFunction:
        return self.contract.functions.disableWhitelist(schain_name)

    def admin_role(self) -> bytes:
        return self.contract.functions.DEFAULT_ADMIN_ROLE().call()

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return self.contract.functions.hasRole(role, address).call()

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.grantRole(role, address)

    def get_role_member(self, role: bytes, index: int) -> bytes:
        return self.contract.functions.getRoleMember(role, index).call()
