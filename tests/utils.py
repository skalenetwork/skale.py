""" SKALE test utilities """

import random
import string
from mock import Mock, MagicMock


def generate_random_ip():
    return '.'.join('%s' % random.randint(0, 255) for i in range(4))


def generate_random_name(len=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=len))


def generate_random_port():
    return random.randint(0, 60000)


def generate_random_node_data():
    return generate_random_ip(), generate_random_ip(), generate_random_port(), \
        generate_random_name()


def generate_random_schain_data():
    lifetime_seconds = 3600  # 1 hour
    type_of_nodes = 4
    return type_of_nodes, lifetime_seconds, generate_random_name()


def response_mock(status_code=0, json_data=None, cookies=None,
                  headers=None, raw=None):
    result = MagicMock()
    result.status_code = status_code
    result.json = MagicMock(return_value=json_data)
    result.cookies = cookies
    result.headers = headers
    result.raw = raw
    return result


def request_mock(response_mock):
    request_mock = Mock(return_value=response_mock)
    return request_mock
