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
from typing import Dict, Tuple

from redis import Redis
from web3 import Web3

from skale.wallets import SgxWallet

logger = logging.getLogger(__name__)


class RedisWallet(SgxWallet):
    ID_SIZE = 12

    def __init__(self,
                 rs: Redis,
                 pool: str,
                 sgx_endpoint: str,
                 web3: Web3,
                 key_name: str = None,
                 path_to_cert: str = None,
                 retry_if_failed: bool = False) -> None:
        super().__init__(sgx_endpoint=sgx_endpoint,
                         web3=web3, key_name=key_name,
                         path_to_cert=path_to_cert)
        self.rs = rs
        self.pool = pool

    @classmethod
    def _make_raw_id(cls) -> bytes:
        prefix = b'tx-'
        time_bytes = int(time.time()).to_bytes(4, 'big').hex().encode('utf-8')
        unique = binascii.b2a_hex(os.urandom(cls.ID_SIZE))
        return prefix + time_bytes + unique

    @classmethod
    def _make_record(cls, tx: Dict, priority: int) -> Tuple[bytes, bytes]:
        tx_id = cls._make_raw_id()
        record = json.dumps({
            'status': 'PROPOSED',
            'priority': priority,
            'tx_hash': None,
            **tx
        }).encode('utf-8')
        return tx_id, record

    @classmethod
    def _to_raw_id(cls, tx_id: str) -> bytes:
        return tx_id.encode('utf-8')

    def _to_id(cls, raw_id: str) -> str:
        return raw_id.decode('utf-8')

    def sign_and_send(self, tx: Dict, priority: int = 1) -> str:
        raw_id, tx_record = self._make_record(tx, priority)
        pipe = self.rs.pipeline()
        pipe.zadd(self.pool, {raw_id: priority})
        pipe.set(raw_id, tx_record)
        pipe.execute()
        return self._to_id(raw_id)

    def get_status(self, tx_id: str) -> str:
        return self.get_record(tx_id)['status']

    def get_record(self, tx_id: str) -> Dict:
        rid = self._to_raw_id(tx_id)
        return json.loads(self.rs.get(rid).decode('utf-8'))

    def wait(self, tx_id: str, timeout: int = 50) -> str:
        start_ts = time.time()
        while time.time() - start_ts < timeout:
            status = self.get_status(tx_id)
            if status in ('SUCCESS', 'FAILED', 'NOT_SENT'):
                return self.get_record(tx_id)
        raise TimeoutError(f'Transaction has not been mined within {timeout}')
