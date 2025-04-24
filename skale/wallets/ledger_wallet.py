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
import struct
from typing import Generator, Tuple, cast

from eth_typing import ChecksumAddress, HexStr
from hexbytes import HexBytes
from eth_account.datastructures import SignedMessage, SignedTransaction
from eth_account._utils.legacy_transactions import (
    encode_transaction,
    serializable_unsigned_transaction_from_dict as tx_from_dict,
    Transaction,
    UnsignedTransaction,
)
from eth_account.typed_transactions.typed_transaction import TypedTransaction

from eth_utils.crypto import keccak
from rlp import encode
from web3 import Web3
from web3.contract.contract import ContractFunction
from web3.exceptions import Web3Exception
from web3.types import _Hash32, TxParams, TxReceipt

import skale.config as config
from skale.transactions.exceptions import TransactionNotSentError, TransactionNotSignedError
from skale.utils.web3_utils import (
    DEFAULT_BLOCKS_TO_WAIT,
    MAX_WAITING_TIME,
    get_eth_nonce,
    public_key_to_address,
    to_checksum_address,
    wait_for_receipt_by_blocks,
)
from skale.wallets.common import BaseWallet, ensure_chain_id

logger = logging.getLogger(__name__)


class LedgerCommunicationError(Exception):
    pass


def encode_bip32_path(path: str) -> bytes:
    if len(path) == 0:
        return b''
    encoded_chunks = []
    for bip32_chunk in path.split('/'):
        chunk = bip32_chunk.split("'")
        if len(chunk) == 1:
            encoded_chunk = struct.pack('>I', int(chunk[0]))
        else:
            encoded_chunk = struct.pack('>I', 0x80000000 | int(chunk[0]))
        encoded_chunks.append(encoded_chunk)

    return b''.join(encoded_chunks)


def derivation_path_prefix(bin32_path: str) -> bytes:
    encoded_path = encode_bip32_path(bin32_path)
    encoded_path_len_bytes = (len(encoded_path) // 4).to_bytes(1, 'big')
    return encoded_path_len_bytes + encoded_path


def chunks(sequence: bytes, size: int) -> Generator[bytes, None, None]:
    return (sequence[pos : pos + size] for pos in range(0, len(sequence), size))


def get_derivation_path(address_index: int, legacy: bool) -> str:
    if legacy:
        return get_legacy_derivation_path(address_index)
    return get_live_derivation_path(address_index)


def get_live_derivation_path(address_index: int) -> str:
    return f"44'/60'/{address_index}'/0/0"


def get_legacy_derivation_path(address_index: int) -> str:
    return f"44'/60'/0'/{address_index}"


class LedgerWallet(BaseWallet):
    CHUNK_SIZE = 255
    CLA = b'\xe0'

    def __init__(self, web3: Web3, address_index: int, legacy: bool = False, debug: bool = False):
        from ledgerblue.comm import getDongle
        from ledgerblue.commException import CommException

        self._address_index = address_index
        self._bip32_path = get_derivation_path(address_index, legacy)
        try:
            self.dongle = getDongle(debug)
            self._web3 = web3
            self._address, self._public_key = self.get_address_with_public_key()
        except (OSError, CommException):
            raise LedgerCommunicationError(
                'Error occured during the interaction with Ledger device'
            )

    @property
    def address(self) -> ChecksumAddress:
        return self._address

    @property
    def public_key(self) -> str:
        return self._public_key

    # todo: remove this method after making software wallet as class
    def __getitem__(self, key: str) -> str:
        items = {'address': self.address, 'public_key': self.public_key}
        return items[key]

    def make_payload(self, data: str = '') -> bytes:
        encoded_data = cast(bytes, encode(data))
        path_prefix = derivation_path_prefix(self._bip32_path)
        return path_prefix + encoded_data

    @classmethod
    def parse_sign_result(
        cls,
        tx: TypedTransaction | Transaction | UnsignedTransaction,
        exchange_result: bytearray | bytes,
    ) -> SignedTransaction:
        sign_v = exchange_result[0]
        sign_r = int((exchange_result[1 : 1 + 32]).hex(), 16)
        sign_s = int((exchange_result[1 + 32 : 1 + 32 + 32]).hex(), 16)
        enctx = encode_transaction(tx, (sign_v, sign_r, sign_s))
        transaction_hash = keccak(enctx)

        return SignedTransaction(
            raw_transaction=HexBytes(enctx),
            hash=HexBytes(transaction_hash),
            v=sign_v,
            r=sign_r,
            s=sign_s,
        )

    def exchange_sign_payload_by_chunks(self, payload: bytes) -> bytearray:
        INS = b'\x04'
        P1_FIRST = b'\x00'
        P1_SUBSEQUENT = b'\x80'
        P2 = b'\x00'

        p1 = P1_FIRST
        for chunk in chunks(payload, LedgerWallet.CHUNK_SIZE):
            chunk_size_bytes = len(chunk).to_bytes(1, 'big')
            apdu = b''.join([LedgerWallet.CLA, INS, p1, P2, chunk_size_bytes, chunk])
            exchange_result = self.dongle.exchange(apdu)
            p1 = P1_SUBSEQUENT
        return cast(bytearray, exchange_result)

    def sign(self, tx_dict: TxParams) -> SignedTransaction:
        ensure_chain_id(tx_dict, self._web3)
        if tx_dict.get('nonce') is None:
            tx_dict['nonce'] = self._web3.eth.get_transaction_count(self.address)

        tx = tx_from_dict(tx_dict)
        try:
            payload = self.make_payload(tx)
            exchange_result = self.exchange_sign_payload_by_chunks(payload)
            return LedgerWallet.parse_sign_result(tx, exchange_result)
        except Exception as e:
            raise TransactionNotSignedError(e)

    def sign_and_send(
        self,
        tx: TxParams,
        multiplier: float | None = config.DEFAULT_GAS_MULTIPLIER,
        priority: int | None = config.DEFAULT_PRIORITY,
        method: str | None = None,
    ) -> HexStr:
        signed_tx = self.sign(tx)
        try:
            return Web3.to_hex(self._web3.eth.send_raw_transaction(signed_tx.raw_transaction))
        except (ValueError, Web3Exception) as e:
            raise TransactionNotSentError(e)

    def sign_hash(self, unsigned_hash: str) -> SignedMessage:
        raise NotImplementedError('sign_hash is not implemented for hardware wallet')

    @classmethod
    def parse_derive_result(cls, exchange_result: bytearray) -> Tuple[ChecksumAddress, str]:
        pk_len = exchange_result[0]
        pk = HexStr(exchange_result[1 : pk_len + 1].hex()[2:])
        address = public_key_to_address(pk)
        checksum_address = to_checksum_address(address)
        return checksum_address, pk

    def exchange_derive_payload(self, payload: bytes) -> bytearray:
        INS = b'\x02'
        P1 = b'\x00'
        P2 = b'\x00'
        payload_size_in_bytes = len(payload).to_bytes(1, 'big')
        apdu = b''.join([LedgerWallet.CLA, INS, P1, P2, payload_size_in_bytes, payload])
        return cast(bytearray, self.dongle.exchange(apdu))

    def get_address_with_public_key(self) -> tuple[ChecksumAddress, str]:
        payload = self.make_payload()
        exchange_result = self.exchange_derive_payload(payload)
        return LedgerWallet.parse_derive_result(exchange_result)

    def wait(
        self,
        tx_hash: _Hash32,
        blocks_to_wait: int = DEFAULT_BLOCKS_TO_WAIT,
        timeout: int = MAX_WAITING_TIME,
    ) -> TxReceipt:
        return wait_for_receipt_by_blocks(
            self._web3, tx_hash, blocks_to_wait=blocks_to_wait, timeout=timeout
        )


def hardware_sign_and_send(
    web3: Web3, method: ContractFunction, gas_amount: int, wallet: LedgerWallet
) -> str:
    address_from = wallet.address
    eth_nonce = get_eth_nonce(web3, address_from)
    tx_dict = method.build_transaction({'gas': gas_amount, 'nonce': eth_nonce})
    signed_txn = wallet.sign(tx_dict)
    tx = web3.eth.send_raw_transaction(signed_txn.raw_transaction).hex()
    logger.info(f'{method.__class__.__name__} - transaction_hash: {tx}')
    return tx
