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

from sgx import SgxClient
from skale.wallets.common import BaseWallet


class SgxWallet(BaseWallet):
    def __init__(self, sgx_endpoint, key_name=None):
        self.sgx_client = SgxClient(sgx_endpoint)
        self.key_name = key_name
        self._address, self._public_key = self._generate()

    def sign(self, tx):
        return self.sgx_client.sign(tx, self.key_name)

    @property
    def address(self):
        return self._address

    @property
    def public_key(self):
        return self._public_key

    def _generate(self):
        account = self.sgx_client.generate_key(self.key_name)
        return (account.address, account.public_key)
