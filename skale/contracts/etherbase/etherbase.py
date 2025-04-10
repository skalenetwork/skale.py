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

from skale.contracts.base_contract import BaseContract, transaction_method
from eth_typing import ChecksumAddress
from skale.transactions.result import TxRes


class Etherbase(BaseContract):
    """Etherbase contract"""

    def default_admin_role(self) -> bytes:
        return self.contract.functions.DEFAULT_ADMIN_ROLE().call()

    def ether_manager_role(self) -> bytes:
        return self.contract.functions.ETHER_MANAGER_ROLE().call()

    @transaction_method
    def retrieve(self, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.retrieve(address)

    @transaction_method
    def partially_retrieve(self, address: ChecksumAddress, amount: int) -> TxRes:
        return self.contract.functions.partiallyRetrieve(address, amount)

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.hasRole(role, address).call())

    def get_role_admin(self, role: bytes) -> bytes:
        return self.contract.functions.getRoleAdmin(role).call()

    def get_role_member(self, role: bytes, index: int) -> bytes:
        return self.contract.functions.getRoleMember(role, index).call()

    def get_role_member_count(self, role: bytes) -> int:
        return self.contract.functions.getRoleMemberCount(role).call()

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.grantRole(role, address)

    @transaction_method
    def revoke_role(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.revokeRole(role, address)

    @transaction_method
    def renounce_role(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.renounceRole(role, address)

    def get_version(self) -> str:
        return self.contract.functions.version().call()

    @transaction_method
    def set_version(self, new_version) -> TxRes:
        return self.contract.functions.setVersion(new_version)
