import functools
import json
import time
import logging
import urllib

import requests

from skale.utils.exceptions import RPCWalletError
from skale.wallets import SgxWallet


logger = logging.getLogger(__name__)


ATTEMPTS = 100
TIMEOUTS = [2 ** p for p in range(ATTEMPTS)]


def rpc_request(func):
    @functools.wraps(func)
    def wrapper(self, route, *args, **kwargs):
        data, error, response = None, None, None
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


class RPCWallet(SgxWallet):
    def __init__(self, url, sgx_endpoint, web3, key_name=None,
                 path_to_cert=None, retry_if_failed=False) -> None:
        super().__init__(sgx_endpoint=sgx_endpoint,
                         web3=web3, key_name=key_name,
                         path_to_cert=path_to_cert)
        self._url = url
        self._retry_if_failed = retry_if_failed

    @classmethod
    def _construct_url(cls, host, url):
        return urllib.parse.urljoin(host, url)

    @rpc_request
    def _post(self, route, data):
        request_url = self._construct_url(self._url, route)
        return requests.post(request_url, json=data)

    @rpc_request
    def _get(self, route, data=None):
        request_url = self._construct_url(self._url, route)
        return requests.get(request_url, data=data)

    @classmethod
    def _compose_tx_data(cls, tx_dict):
        return {
            'transaction_dict': json.dumps(tx_dict)
        }

    def sign_and_send(self, tx_dict):
        data = self._post('/sign-and-send',
                          self._compose_tx_data(tx_dict))
        return data['transaction_hash']
