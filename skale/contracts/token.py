#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" SKALE token operations """

from skale.contracts import BaseContract
from skale.utils.constants import GAS
from skale.utils.helper import sign_and_send


class Token(BaseContract):
    def transfer(self, address, value, wallet):
        op = self.contract.functions.transfer(address, value)
        tx = sign_and_send(self.skale, op, GAS['token_transfer'], wallet)
        return {'tx': tx}

    def get_balance(self, address):
        return self.contract.functions.balanceOf(address).call()

    def add_authorized(self, address, wallet):
        op = self.contract.functions.addAuthorized(address)
        tx = sign_and_send(self.skale, op, GAS['token_transfer'], wallet)
        return {'tx': tx}
