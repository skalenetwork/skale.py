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

from eth_keys import keys
from web3 import Web3
from eth_account import messages

from skale.wallets.common import BaseWallet
from skale.utils.web3_utils import get_eth_nonce


def private_key_to_public(pr):
    pr_bytes = Web3.toBytes(hexstr=pr)
    pk = keys.PrivateKey(pr_bytes)
    return pk.public_key


def public_key_to_address(pk):
    hash = Web3.keccak(hexstr=str(pk))
    return to_checksum_address(Web3.toHex(hash[-20:]))


def private_key_to_address(pr):
    pk = private_key_to_public(pr)
    return public_key_to_address(pk)


def to_checksum_address(address):
    return Web3.toChecksumAddress(address)


def generate_wallet(web3):
    account = web3.eth.account.create()
    private_key = account.key.hex()
    return Web3Wallet(private_key, web3)


class Web3Wallet(BaseWallet):
    def __init__(self, private_key, web3):
        self._private_key = private_key
        self._public_key = private_key_to_public(self._private_key)
        self._address = public_key_to_address(self._public_key)

        self._web3 = web3

    def sign(self, tx_dict):
        if not tx_dict.get('nonce'):
            tx_dict['nonce'] = get_eth_nonce(self._web3, self._address)
        return self._web3.eth.account.sign_transaction(
            tx_dict,
            private_key=self._private_key
        )

    def sign_hash(self, unsigned_hash: str):
        unsigned_message = messages.encode_defunct(hexstr=unsigned_hash)
        return self._web3.eth.account.sign_message(
            unsigned_message,
            private_key=self._private_key
        )

    def sign_and_send(self, tx_dict) -> str:
        signed_tx = self.sign(tx_dict)
        return self._web3.eth.sendRawTransaction(signed_tx.rawTransaction).hex()

    @property
    def address(self):
        return self._address

    @property
    def public_key(self):
        return str(self._public_key)
