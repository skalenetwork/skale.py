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

import logging

from sgx import SgxClient
from web3 import Web3

from skale.utils.web3_utils import get_eth_nonce
from skale.wallets.common import BaseWallet


logger = logging.getLogger(__name__)


class SgxWallet(BaseWallet):
    def __init__(self, sgx_endpoint, web3, key_name=None, path_to_cert=None):
        self.sgx_client = SgxClient(sgx_endpoint, path_to_cert=path_to_cert)
        self._web3 = web3
        if key_name is None:
            self._key_name, self._address, self._public_key = self._generate()
        else:
            self._key_name = key_name
            self._address, self._public_key = self._get_account(key_name)

    def sign(self, tx_dict):
        if tx_dict.get('nonce') is None:
            tx_dict['nonce'] = get_eth_nonce(self._web3, self._address)
        return self.sgx_client.sign(tx_dict, self.key_name)

    def sign_and_send(self, tx_dict) -> str:
        signed_tx = self.sign(tx_dict)
        return self._web3.eth.sendRawTransaction(signed_tx.rawTransaction).hex()

    def sign_hash(self, unsigned_hash: str):
        if unsigned_hash.startswith('0x'):
            unsigned_hash = unsigned_hash[2:]

        body = bytes.fromhex(unsigned_hash)
        header = b'\x19Ethereum Signed Message:\n32'
        normalized_hash = header + body
        hash_to_sign = Web3.keccak(hexstr='0x' + normalized_hash.hex())
        chain_id = None
        return self.sgx_client.sign_hash(hash_to_sign, self._key_name, chain_id)

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
