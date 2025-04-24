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
from typing import Tuple, cast

from eth_account.datastructures import SignedMessage, SignedTransaction
from eth_typing import ChecksumAddress, HexStr
from sgx import SgxClient
from web3 import Web3
from web3.exceptions import Web3Exception
from web3.types import _Hash32, TxParams, TxReceipt

import skale.config as config
from skale.transactions.exceptions import TransactionNotSentError, TransactionNotSignedError
from skale.utils.web3_utils import (
    DEFAULT_BLOCKS_TO_WAIT,
    MAX_WAITING_TIME,
    get_eth_nonce,
    wait_for_receipt_by_blocks,
)
from skale.wallets.common import BaseWallet, ensure_chain_id, MessageNotSignedError


logger = logging.getLogger(__name__)


class SgxWallet(BaseWallet):
    def __init__(
        self,
        sgx_endpoint: str,
        web3: Web3,
        key_name: str | None = None,
        path_to_cert: str | None = None,
    ):
        self.sgx_client = SgxClient(sgx_endpoint, path_to_cert=path_to_cert)
        self._web3 = web3
        if key_name is None:
            self._key_name, self._address, self._public_key = self._generate()
        else:
            self._key_name = key_name
            self._address, self._public_key = self._get_account(key_name)

    def sign(self, tx_dict: TxParams) -> SignedTransaction:
        if tx_dict.get('nonce') is None:
            tx_dict['nonce'] = get_eth_nonce(self._web3, self._address)
        ensure_chain_id(tx_dict, self._web3)
        try:
            return cast(SignedTransaction, self.sgx_client.sign(tx_dict, self.key_name))
        except Exception as e:
            raise TransactionNotSignedError(e)

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

    def sign_hash(self, unsigned_hash: str) -> SignedMessage:
        if unsigned_hash.startswith('0x'):
            unsigned_hash = unsigned_hash[2:]

        body = bytes.fromhex(unsigned_hash)
        header = b'\x19Ethereum Signed Message:\n32'
        normalized_hash = header + body
        hash_to_sign = Web3.keccak(hexstr='0x' + normalized_hash.hex())
        chain_id = None
        try:
            return cast(
                SignedMessage, self.sgx_client.sign_hash(hash_to_sign, self._key_name, chain_id)
            )
        except Exception as e:
            raise MessageNotSignedError(e)

    @property
    def address(self) -> ChecksumAddress:
        return self._address

    @property
    def public_key(self) -> str:
        return self._public_key

    @property
    def key_name(self) -> str:
        return self._key_name

    def _generate(self) -> Tuple[str, ChecksumAddress, str]:
        key = self.sgx_client.generate_key()
        return key.name, Web3.to_checksum_address(key.address), key.public_key

    def _get_account(self, key_name: str) -> Tuple[ChecksumAddress, str]:
        account = self.sgx_client.get_account(key_name)
        return Web3.to_checksum_address(account.address), account.public_key

    def wait(
        self,
        tx_hash: _Hash32,
        blocks_to_wait: int = DEFAULT_BLOCKS_TO_WAIT,
        timeout: int = MAX_WAITING_TIME,
    ) -> TxReceipt:
        return wait_for_receipt_by_blocks(
            self._web3, tx_hash, blocks_to_wait=blocks_to_wait, timeout=timeout
        )
