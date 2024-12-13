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


class Context(BaseContract):
    """Context contract"""

    def get_schain_name(self) -> str:
        return self.contract.functions.getSchainName().call()

    def get_schain_owner_address(self) -> bytes:
        return self.contract.functions.getSchainOwnerAddress().call()

    @transaction_method
    def set_schain_owner_address(self, newOwner: ChecksumAddress) -> TxRes:
        return self.contract.functions.setSchainOwnerAddress(newOwner)

    def get_version(self) -> str:
        return self.contract.functions.version().call()
