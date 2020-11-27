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

import functools
import json
import logging
import time
import urllib

import requests
from hexbytes import HexBytes
from eth_account.datastructures import AttributeDict

from skale.wallets.common import BaseWallet
from skale.utils.exceptions import RPCWalletError


logger = logging.getLogger(__name__)

ROUTES = {
    'sign': '/sign',
    'sign_and_send': '/sign-and-send',
    'sign_hash': '/sign-hash',
    'address': '/address',
    'public_key': '/public-key',
}

ATTEMPTS = 10
TIMEOUTS = [2 ** p for p in range(ATTEMPTS)]
SGX_UNREACHABLE_MESSAGE = 'Sgx server is unreachable'


def rpc_request(func):
    @functools.wraps(func)
    def wrapper(self, route, *args, **kwargs):
        data, error = None, None
        for i, timeout in enumerate(TIMEOUTS):
            logger.info(f'Sending request to tm for {route}. Try {i}')
            try:
                response = func(self, route, *args, **kwargs).json()
                data, error = response.get('data'), response.get('error')
            except Exception as err:
                error = 'RPC request failed'
                logger.error(error, exc_info=err)

            if not error or not self._retry_if_failed:
                break

            logger.info(f'Sleeping {timeout}s ...')
            time.sleep(timeout)

        if error is not None:
            raise RPCWalletError(error)
        return data
    return wrapper


class RPCWallet(BaseWallet):
    def __init__(self, url, retry_if_failed=False):
        self._url = url
        self._retry_if_failed = retry_if_failed

    def _construct_url(self, host, url):
        return urllib.parse.urljoin(host, url)

    @rpc_request
    def _post(self, route, data):
        request_url = self._construct_url(self._url, route)
        return requests.post(request_url, json=data)

    @rpc_request
    def _get(self, route, data=None):
        request_url = self._construct_url(self._url, route)
        return requests.get(request_url, data=data)

    def _compose_tx_data(self, tx_dict):
        return {
            'transaction_dict': json.dumps(tx_dict)
        }

    def sign(self, tx_dict):
        data = self._post(ROUTES['sign'], self._compose_tx_data(tx_dict))
        return AttributeDict(data)

    def sign_and_send(self, tx_dict):
        data = self._post(ROUTES['sign_and_send'], self._compose_tx_data(tx_dict))
        return data['transaction_hash']

    def sign_hash(self, unsigned_hash: str):
        data = self._post(ROUTES['sign_hash'], {'unsigned_hash': unsigned_hash})
        return AttributeDict({
            'messageHash': HexBytes(data['messageHash']),
            'r': data['r'],
            's': data['s'],
            'v': data['v'],
            'signature': HexBytes(data['signature']),
        })

    @property
    def address(self):
        data = self._get(ROUTES['address'])
        return data['address']

    @property
    def public_key(self):
        data = self._get(ROUTES['public_key'])
        return data['public_key']
