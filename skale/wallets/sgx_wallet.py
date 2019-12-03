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

from sgx import SgxClient
from skale.wallets.common import BaseWallet


class SgxWallet(BaseWallet):
    def __init__(self, sgx_endpoint, web3, key_name=None):
        self.sgx_client = SgxClient(sgx_endpoint)
        self._web3 = web3
        if key_name is None:
            self._key_name, self._address, self._public_key = self._generate()
        else:
            self._key_name = key_name
            self._address, self._public_key = self._get_account(key_name)

    def sign(self, tx):
        return self.sgx_client.sign(tx, self.key_name)

    def sign_and_send(self, tx):
        signed_tx = self.sgx_client.sign(tx, self.key_name)
        return self._web3.eth.sendRawTransaction(signed_tx.rawTransaction)

    @property
    def address(self):
        return self._address

    @property
    def public_key(self):
        return self._public_key

    @property
    def key_name(self):
        return self._key_name

    def _generate(self):
        key = self.sgx_client.generate_key()
        return key.name, key.address, key.public_key

    def _get_account(self, key_name):
        account = self.sgx_client.get_account(key_name)
        return account.address, account.public_key
