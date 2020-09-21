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
""" SKALE token operations """

from skale.contracts.base_contract import BaseContract, transaction_method


class Token(BaseContract):
    @transaction_method
    def transfer(self, address, value):
        return self.contract.functions.send(address, value, b'')

    def get_balance(self, address):
        return self.contract.functions.balanceOf(address).call()

    @transaction_method
    def add_authorized(self, address, wallet):  # pragma: no cover
        return self.contract.functions.addAuthorized(address)

    def get_and_update_slashed_amount(self, address: str) -> int:
        return self.contract.functions.getAndUpdateSlashedAmount(address).call()

    @transaction_method
    def mint(self, address, amount, user_data=b'', operator_data=b''):
        return self.contract.functions.mint(address, amount, user_data, operator_data)
