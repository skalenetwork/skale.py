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


class MessageProxyForSchain(BaseContract):
    @transaction_method
    def set_minimum_receiver_balance(self, amount: int) -> TxRes:
        return self.contract.functions.setMinimumReceiverBalance(amount)

    def get_minimum_receiver_balance(self) -> int:
        return self.contract.functions.minimumReceiverBalance().call()

    def constant_setter_role(self) -> bytes:
        return self.contract.functions.CONSTANT_SETTER_ROLE().call()

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return self.contract.functions.hasRole(role, address).call()

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.grantRole(role, address)
