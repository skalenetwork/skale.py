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

from eth_keys import keys
from web3 import Web3

from skale.wallets.common import BaseWallet


def private_key_to_public(pr):
    pr_bytes = Web3.toBytes(hexstr=pr)
    pk = keys.PrivateKey(pr_bytes)
    return pk.public_key


def public_key_to_address(pk):
    hash = Web3.sha3(hexstr=str(pk))
    return to_checksum_address(Web3.toHex(hash[-20:]))


def private_key_to_address(pr):
    pk = private_key_to_public(pr)
    return public_key_to_address(pk)


def to_checksum_address(address):
    return Web3.toChecksumAddress(address)


class Web3Wallet(BaseWallet):
    def __init__(self, private_key, web3):
        self._private_key = private_key
        self._public_key = private_key_to_public(self._private_key)
        self._address = public_key_to_address(self._public_key)

        self._web3 = web3

    def sign(self, tx_dict):
        return self._web3.eth.account.sign_transaction(
            tx_dict,
            private_key=self._private_key
        )

    @property
    def address(self):
        return self._address

    @property
    def public_key(self):
        return self._public_key