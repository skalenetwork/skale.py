#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2025-Present SKALE Labs
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

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any, Mapping

from redis import Redis
from redis.exceptions import RedisError
from web3.middleware.base import Web3Middleware

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RedisCacheConfig:
    redis_url: str
    cache_methods: frozenset[str]
    bypass_addresses: frozenset[str] = frozenset()
    default_ttl_seconds: int = 2
    key_prefix: str = 'rpc-cache:v1'
    method_ttl_policy: Mapping[str, int] | None = None


def ttl_policy(
    method: str,
    params: list[Any],
    default_ttl_seconds: int,
    method_ttl_policy: Mapping[str, int] | None = None,
) -> int:
    method_default_ttl = (
        method_ttl_policy[method]
        if method_ttl_policy is not None and method in method_ttl_policy
        else default_ttl_seconds
    )

    if method_default_ttl <= 0:
        return 0

    block_id = _extract_block_identifier(method, params)
    if isinstance(block_id, int):
        return 60
    if isinstance(block_id, str):
        if block_id.startswith('0x'):
            return 60
        if block_id in {'latest', 'safe', 'finalized'}:
            return method_default_ttl
        if block_id == 'pending':
            return 0

    return method_default_ttl


def redis_cache_middleware(config: RedisCacheConfig) -> type[Web3Middleware]:
    redis = Redis.from_url(config.redis_url)
    cache_methods = {m for m in config.cache_methods}
    bypass_addresses = {_normalize_address(a) for a in config.bypass_addresses}
    disallowed = {
        'eth_getLogs',
        'eth_sendRawTransaction',
        'eth_sendTransaction',
        'personal_sendTransaction',
        'eth_sign',
        'eth_signTransaction',
        'eth_signTypedData',
        'eth_signTypedData_v3',
        'eth_signTypedData_v4',
    }

    class _RedisCacheMiddleware(Web3Middleware):
        def wrap_make_request(self, make_request):
            endpoint = getattr(self._w3.provider, 'endpoint_uri', '') or ''
            endpoint_hash = hashlib.sha256(endpoint.encode('utf-8')).hexdigest()[:16]

            def request(method: str, params: list[Any]):
                if method in disallowed or method not in cache_methods:
                    return make_request(method, params)

                if method == 'eth_getTransactionCount' and _is_pending_tx_count(params):
                    return make_request(method, params)

                if method in {'eth_call', 'eth_estimateGas'} and _is_bypassed_address(
                    params, bypass_addresses
                ):
                    return make_request(method, params)

                ttl_seconds = ttl_policy(
                    method,
                    params,
                    config.default_ttl_seconds,
                    config.method_ttl_policy,
                )
                if ttl_seconds <= 0:
                    return make_request(method, params)

                key = _cache_key(
                    prefix=config.key_prefix,
                    endpoint_hash=endpoint_hash,
                    method=method,
                    params=params,
                )

                try:
                    cached = redis.get(key)
                except (OSError, RedisError):
                    cached = None

                if cached:
                    try:
                        return json.loads(cached)
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        pass

                response = make_request(method, params)
                if isinstance(response, dict) and 'error' not in response and 'result' in response:
                    try:
                        payload = json.dumps(
                            response, separators=(',', ':'), sort_keys=True
                        ).encode('utf-8')
                        redis.setex(key, ttl_seconds, payload)
                    except (RedisError, ValueError, UnicodeEncodeError):
                        pass

                return response

            return request

    return _RedisCacheMiddleware


def _cache_key(prefix: str, endpoint_hash: str, method: str, params: list[Any]) -> str:
    body = json.dumps(
        {'method': method, 'params': params},
        separators=(',', ':'),
        sort_keys=True,
        default=_json_default,
    ).encode('utf-8')
    request_hash = hashlib.sha256(body).hexdigest()
    return f'{prefix}:{endpoint_hash}:{request_hash}'


def _json_default(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray, memoryview)):
        return '0x' + bytes(value).hex()
    if hasattr(value, 'hex'):
        try:
            return value.hex()
        except (TypeError, ValueError):
            return str(value)
    return str(value)


def _normalize_address(address: str) -> str:
    address = address.strip().lower()
    if address.startswith('0x'):
        return address
    return '0x' + address


def _is_bypassed_address(params: list[Any], bypass_addresses: set[str]) -> bool:
    if not bypass_addresses or not params:
        return False
    tx = params[0]
    if not isinstance(tx, dict):
        return False
    to_addr = tx.get('to')
    if not isinstance(to_addr, str):
        return False
    return _normalize_address(to_addr) in bypass_addresses


def _is_pending_tx_count(params: list[Any]) -> bool:
    if len(params) < 2:
        return False
    block_id = params[1]
    return block_id == 'pending'


def _extract_block_identifier(method: str, params: list[Any]) -> Any:
    if method in {'eth_call', 'eth_estimateGas'}:
        return params[1] if len(params) > 1 else 'latest'
    if method in {'eth_getBalance', 'eth_getCode', 'eth_getStorageAt', 'eth_getTransactionCount'}:
        return params[1] if len(params) > 1 else 'latest'
    return None
