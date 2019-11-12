import json
import logging
import urllib
import requests

LOGGER = logging.getLogger(__name__)


class TransactionsManager():
    def __init__(self, tm_url):
        self.tm_url = tm_url

    def send_transaction(self, transaction_dict):
        return self.post(transaction_dict)

    def construct_url(self, host, url):
        return urllib.parse.urljoin(host, url)

    def post(self, transaction_dict):
        url = self.construct_url(self.tm_url, 'sign-and-send')
        request_json = {
            'transaction_dict': json.dumps(transaction_dict)
        }
        try:
            response = requests.post(url, json=request_json)
        except requests.exceptions.ConnectionError as e:
            LOGGER.exception(f'Unable to connect to the transactions manager: {self.tm_url}')
            raise e

        if response.status_code != requests.codes.ok:
            print('Request failed, status code:', response.status_code)
            return None

        resp_json = response.json()
        if resp_json['res'] != 1:
            LOGGER.error('Response contains errors, check out response values.')
            return response.json()
        else:
            return resp_json['data']
