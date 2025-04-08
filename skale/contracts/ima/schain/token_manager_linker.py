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
from skale.transactions.result import TxRes
from eth_typing import ChecksumAddress


class TokenManagerLinker(BaseContract):
    """Linker"""

    @transaction_method
    def connect_schain(self, schain_name) -> TxRes:
        return self.contract.functions.connectSchain(schain_name)

    @transaction_method
    def disconnect_schain(self, schain_name) -> TxRes:
        return self.contract.functions.disconnectSchain(schain_name)

    def has_schain(self, schian_name) -> bool:
        return self.contract.functions.hasSchain(schian_name).call()

    def registrar_role(self) -> bytes:
        return self.contract.functions.REGISTRAR_ROLE().call()

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return self.contract.functions.hasRole(role, address).call()

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.grantRole(role, address)
