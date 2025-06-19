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

from typing import cast
from eth_keys.main import lazy_key_api as keys
from eth_keys.datatypes import PublicKey
from web3 import Web3
from web3.types import _Hash32, TxParams, TxReceipt
from eth_account import messages
from eth_account.datastructures import SignedMessage, SignedTransaction
from eth_typing import AnyAddress, ChecksumAddress, HexStr
from web3.exceptions import Web3Exception

import skale.config as config
from skale.transactions.exceptions import TransactionNotSignedError, TransactionNotSentError
from skale.utils.web3_utils import (
    DEFAULT_BLOCKS_TO_WAIT,
    MAX_WAITING_TIME,
    get_eth_nonce,
    wait_for_receipt_by_blocks,
)
from skale.wallets.common import BaseWallet, ensure_chain_id, MessageNotSignedError


def private_key_to_public(pr: HexStr) -> PublicKey:
    pr_bytes = Web3.to_bytes(hexstr=pr)
    pk = keys.PrivateKey(pr_bytes)
    return pk.public_key


def public_key_to_address(pk: PublicKey) -> ChecksumAddress:
    hash = Web3.keccak(hexstr=str(pk))
    return to_checksum_address(Web3.to_hex(hash[-20:]))


def private_key_to_address(pr: HexStr) -> ChecksumAddress:
    pk = private_key_to_public(pr)
    return public_key_to_address(pk)


def to_checksum_address(address: AnyAddress | str | bytes) -> ChecksumAddress:
    return Web3.to_checksum_address(address)


class Web3Wallet(BaseWallet):
    def __init__(self, private_key: HexStr, web3: Web3):
        self._private_key = private_key
        self._public_key = private_key_to_public(self._private_key)
        self._address = public_key_to_address(self._public_key)

        self._web3 = web3

    def sign(self, tx_dict: TxParams) -> SignedTransaction:
        if not tx_dict.get('nonce'):
            tx_dict['nonce'] = get_eth_nonce(self._web3, self._address)
        ensure_chain_id(tx_dict, self._web3)
        try:
            return cast(
                SignedTransaction,
                self._web3.eth.account.sign_transaction(tx_dict, private_key=self._private_key),
            )
        except (TypeError, ValueError, Web3Exception) as e:
            raise TransactionNotSignedError(e)

    def sign_hash(self, unsigned_hash: str) -> SignedMessage:
        try:
            unsigned_message = messages.encode_defunct(hexstr=unsigned_hash)
            return cast(
                SignedMessage,
                self._web3.eth.account.sign_message(
                    unsigned_message, private_key=self._private_key
                ),
            )
        except (TypeError, ValueError, Web3Exception) as e:
            raise MessageNotSignedError(e)

    def sign_and_send(
        self,
        tx_dict: TxParams,
        multiplier: float | None = config.DEFAULT_GAS_MULTIPLIER,
        priority: int | None = config.DEFAULT_PRIORITY,
        method: str | None = None,
    ) -> HexStr:
        signed_tx = self.sign(tx_dict)
        try:
            return Web3.to_hex(self._web3.eth.send_raw_transaction(signed_tx.raw_transaction))
        except (ValueError, Web3Exception) as e:
            raise TransactionNotSentError(e)

    @property
    def address(self) -> ChecksumAddress:
        return self._address

    @property
    def public_key(self) -> str:
        return str(self._public_key)

    def wait(
        self,
        tx_hash: _Hash32,
        blocks_to_wait: int = DEFAULT_BLOCKS_TO_WAIT,
        timeout: int = MAX_WAITING_TIME,
    ) -> TxReceipt:
        return wait_for_receipt_by_blocks(
            self._web3, tx_hash, blocks_to_wait=blocks_to_wait, timeout=timeout
        )


def generate_wallet(web3: Web3) -> Web3Wallet:
    account = web3.eth.account.create()
    private_key = account.key.hex()
    return Web3Wallet(private_key, web3)


def generate_wallets(web3: Web3, n_of_keys: int) -> list[Web3Wallet]:
    return [generate_wallet(web3) for _ in range(n_of_keys)]
