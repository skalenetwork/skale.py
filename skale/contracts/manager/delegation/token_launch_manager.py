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


class TokenLaunchManager(BaseContract):
    """Wrapper for TokenLaunchManager.sol functions"""

    @transaction_method
    def approve_batch_of_transfers(self, wallet_addresses, values):
        if len(wallet_addresses) != len(values):
            raise ValueError('wallet_addresses and values length do not match')
        return self.contract.functions.approveBatchOfTransfers(wallet_addresses, values)

    @transaction_method
    def approve_transfer(self, wallet_address, value):
        return self.contract.functions.approveBatchOfTransfers(wallet_address, value)

    @transaction_method
    def retrieve(self):
        return self.contract.functions.retrieve()

    @transaction_method
    def complete_token_launch(self):
        return self.contract.functions.completeTokenLaunch()

    def approved(self, address: str) -> int:
        return self.contract.functions.approved(address).call()
