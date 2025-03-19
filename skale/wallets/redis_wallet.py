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

import binascii
import json
import logging
import os
import time
from enum import Enum
from typing import Optional, Tuple, TypedDict

from eth_account.datastructures import SignedMessage, SignedTransaction
from eth_typing import ChecksumAddress, HexStr
from redis import Redis
from web3 import Web3
from web3.types import _Hash32, TxParams, TxReceipt

import skale.config as config
from skale.transactions.exceptions import (
    TransactionError,
    TransactionNotMinedError,
    TransactionNotSentError,
    TransactionWaitError,
)
from skale.utils.web3_utils import DEFAULT_BLOCKS_TO_WAIT, get_receipt, MAX_WAITING_TIME
from skale.wallets import BaseWallet
from skale.wallets.web3_wallet import Web3Wallet

logger = logging.getLogger(__name__)


class RedisWalletError(Exception):
    pass


class RedisWalletDroppedError(RedisWalletError, TransactionNotMinedError):
    pass


class RedisWalletEmptyStatusError(RedisWalletError, TransactionError):
    pass


class RedisWalletNotSentError(RedisWalletError, TransactionNotSentError):
    pass


class RedisWalletWaitError(RedisWalletError, TransactionWaitError):
    pass


class TxRecordStatus(str, Enum):
    DROPPED = 'DROPPED'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'

    def __str__(self) -> str:
        return str.__str__(self)


TxRecord = TypedDict(
    'TxRecord',
    {'status': TxRecordStatus, 'tx_hash': HexStr},
)


class RedisWalletAdapter(BaseWallet):
    ID_SIZE = 16

    def __init__(
        self,
        rs: Redis,
        pool: str,
        web3_wallet: Web3Wallet,
    ) -> None:
        self.rs = rs
        self.pool = pool
        self.wallet = web3_wallet

    def sign(self, tx: TxParams) -> SignedTransaction:
        return self.wallet.sign(tx)

    def sign_hash(self, unsigned_hash: str) -> SignedMessage:
        return self.wallet.sign_hash(unsigned_hash)

    @property
    def address(self) -> ChecksumAddress:
        return self.wallet.address

    @property
    def public_key(self) -> str:
        return self.wallet.public_key

    @classmethod
    def _make_raw_id(cls) -> bytes:
        prefix = b'tx-'
        unique = binascii.b2a_hex(os.urandom(cls.ID_SIZE // 2))
        return prefix + unique

    @classmethod
    def _make_score(cls, priority: int) -> int:
        ts = int(time.time())
        return priority * int(10 ** len(str(ts))) + ts

    @classmethod
    def _make_record(
        cls,
        tx: TxParams,
        score: int,
        multiplier: float = config.DEFAULT_GAS_MULTIPLIER,
        method: Optional[str] = None,
    ) -> Tuple[bytes, bytes]:
        tx_id = cls._make_raw_id()
        params = {
            'status': 'PROPOSED',
            'score': score,
            'multiplier': multiplier,
            'tx_hash': None,
            'method': method,
            **tx,
        }
        # Ensure gas will be restimated in TM
        params['gas'] = None
        record = json.dumps(params).encode('utf-8')
        return tx_id, record

    @classmethod
    def _to_raw_id(cls, tx_id: _Hash32) -> bytes:
        if isinstance(tx_id, str):
            return Web3.to_bytes(hexstr=tx_id)
        return Web3.to_bytes(tx_id)

    @classmethod
    def _to_id(cls, raw_id: bytes) -> HexStr:
        return Web3.to_hex(raw_id)

    def sign_and_send(
        self,
        tx: TxParams,
        multiplier: Optional[float] = None,
        priority: Optional[int] = None,
        method: Optional[str] = None,
    ) -> HexStr:
        priority = priority or config.DEFAULT_PRIORITY
        try:
            logger.info('Sending %s to redis pool, method: %s', tx, method)
            score = self._make_score(priority)
            raw_id, tx_record = self._make_record(
                tx, score, multiplier=multiplier or config.DEFAULT_GAS_MULTIPLIER, method=method
            )
            pipe = self.rs.pipeline()
            logger.info('Adding tx %s to the pool', raw_id)
            pipe.zadd(self.pool, {raw_id: score})
            logger.info('Saving tx %s record: %s', raw_id, tx_record)
            pipe.set(raw_id, tx_record, ex=config.TXRECORD_EXPIRATION)
            pipe.execute()
            return self._to_id(raw_id)
        except Exception as err:
            logger.exception(f'Sending {tx} with redis wallet errored')
            raise RedisWalletNotSentError(err)

    def get_status(self, tx_id: _Hash32) -> str:
        return self.get_record(tx_id)['status']

    def get_record(self, tx_id: _Hash32) -> TxRecord:
        rid = self._to_raw_id(tx_id)
        response = self.rs.get(rid)
        if isinstance(response, bytes):
            parsed_json = json.loads(response.decode('utf-8'))
            return TxRecord({'status': parsed_json['status'], 'tx_hash': parsed_json['tx_hash']})
        raise ValueError('Unknown value was returned from get() call', response)

    def wait(
        self,
        tx_id: _Hash32,
        blocks_to_wait: int = DEFAULT_BLOCKS_TO_WAIT,
        timeout: int = MAX_WAITING_TIME,
    ) -> TxReceipt:
        start_ts = time.time()
        status, result = None, None
        while (
            status not in [TxRecordStatus.DROPPED, TxRecordStatus.SUCCESS, TxRecordStatus.FAILED]
            and time.time() - start_ts < timeout
        ):
            try:
                record = self.get_record(tx_id)
                if record is not None:
                    status = record.get('status')
                    if status in (TxRecordStatus.SUCCESS, TxRecordStatus.FAILED):
                        result = get_receipt(self.wallet._web3, record['tx_hash'])
            except Exception as e:
                logger.exception('Waiting for tx %s errored', tx_id)
                raise RedisWalletWaitError(e)

        if result:
            return result

        if status is None:
            raise RedisWalletEmptyStatusError(f'Tx status is {status}')
        elif status == TxRecordStatus.DROPPED:
            raise RedisWalletDroppedError('Tx was dropped after max retries')
        else:
            raise RedisWalletWaitError(f'Tx finished with status {status}')
