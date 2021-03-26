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
from skale.utils.web3_utils import to_checksum_address

DEFAULT_TOKEN_MANAGER_ADDRESS = '0x57ad607c6e90df7d7f158985c3e436007a15d744'


class LockAndData(BaseContract):
    @transaction_method
    def add_schain(self, schain_name, token_manager_address=DEFAULT_TOKEN_MANAGER_ADDRESS):
        address_fx = to_checksum_address(token_manager_address)
        return self.contract.functions.addSchain(
            schain_name,
            address_fx
        )
