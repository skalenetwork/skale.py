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

import json
from collections import Counter
from dataclasses import dataclass, field
from threading import Lock
from typing import Any

import requests


@dataclass(slots=True)
class RpcHttpStats:
    http_posts: int = 0
    rpc_objects: int = 0
    by_method: Counter[str] = field(default_factory=Counter)
    transport_errors: int = 0


class CountingSession(requests.Session):
    def __init__(self, stats: RpcHttpStats):
        super().__init__()
        self.stats = stats
        self._lock = Lock()

    def request(self, *args: Any, **kwargs: Any) -> requests.Response:
        method = str(args[0]) if args else str(kwargs.get('method', ''))
        if method.upper() == 'POST':
            n, methods = _count_jsonrpc(kwargs)
            with self._lock:
                self.stats.http_posts += 1
                self.stats.rpc_objects += n
                self.stats.by_method.update(methods)
            try:
                return super().request(*args, **kwargs)
            except Exception:
                with self._lock:
                    self.stats.transport_errors += 1
                raise

        return super().request(*args, **kwargs)


def _count_jsonrpc(kwargs: dict[str, Any]) -> tuple[int, list[str]]:
    payload = kwargs.get('json')
    if payload is None:
        data = kwargs.get('data')
        if isinstance(data, (bytes, bytearray)):
            data = data.decode('utf-8', errors='replace')
        if isinstance(data, str):
            try:
                payload = json.loads(data)
            except Exception:
                return 0, []

    if isinstance(payload, dict):
        method = payload.get('method')
        return 1, [method] if isinstance(method, str) else []

    if isinstance(payload, list):
        methods = [obj.get('method') for obj in payload if isinstance(obj, dict)]
        return len(payload), [method for method in methods if isinstance(method, str)]

    return 0, []
