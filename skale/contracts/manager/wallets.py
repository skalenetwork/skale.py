#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2021-Present SKALE Labs
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


class Wallets(BaseContract):
    def get_validator_balance(self, validator_id: int) -> int:
        """Returns SRW balance by validator id (in wei).

        :returns: SRW balance (wei)
        :rtype: int
        """
        return self.contract.functions.getValidatorBalance(validator_id).call()

    @transaction_method
    def recharge_validator_wallet(self, validator_id: int) -> TxRes:
        """Pass value kwarg (in wei) to the function when calling it"""
        return self.contract.functions.rechargeValidatorWallet(validator_id)

    @transaction_method
    def withdraw_funds_from_validator_wallet(self, amount: int) -> TxRes:
        return self.contract.functions.withdrawFundsFromValidatorWallet(amount)
