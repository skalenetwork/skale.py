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

import json
import logging
import urllib
import functools
import requests

from hexbytes import HexBytes
from eth_account.datastructures import AttributeDict

from skale.wallets.common import BaseWallet
from skale.utils.exceptions import RPCWalletError


LOGGER = logging.getLogger(__name__)

ROUTES = {
    'sign': '/sign',
    'sign_and_send': '/sign-and-send',
    'sign_hash': '/sign-hash',
    'address': '/address',
    'public_key': '/public-key',
}


def rpc_request(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        res = func(*args, **kwargs)
        res_json = res.json()
        if res_json['error']:
            raise RPCWalletError(res_json['error'])
        else:
            return res_json['data']
    return wrapper_decorator


class RPCWallet(BaseWallet):
    def __init__(self, url):
        self._url = url

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
        return data['transaction_hash']

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
