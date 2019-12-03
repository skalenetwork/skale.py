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

from skale.contracts import BaseContract
from skale.transactions.tools import post_transaction
from skale.utils.constants import GAS


class Token(BaseContract):
    def transfer(self, address, value):
        op = self.contract.functions.send(address, value, b'')
        tx = post_transaction(self.skale.wallet, op, GAS['token_transfer'])
        return {'tx': tx}

    def get_balance(self, address):
        return self.contract.functions.balanceOf(address).call()

    def add_authorized(self, address, wallet):  # pragma: no cover
        op = self.contract.functions.addAuthorized(address)
        tx = post_transaction(self.skale.wallet, op, GAS['token_transfer'])
        return {'tx': tx}
