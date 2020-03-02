""" SKALE test utilities """

from mock import Mock, MagicMock


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
    return Mock(return_value=response_mock)
