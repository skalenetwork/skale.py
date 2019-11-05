from skale.utils.helper import format_fields, is_valid_ipv4_address


def test_format():
    values = ['value1', 'value2']

    @format_fields(['key1', 'key2'])
    def simple_function():
        return values

    assert simple_function() == {'key1': 'value1', 'key2': 'value2'}

    values = None

    assert simple_function() is None


def test_is_valid_ipv4_address():
    assert is_valid_ipv4_address('1.1.1.1') is True
    assert is_valid_ipv4_address('1.1.1') is False
    assert is_valid_ipv4_address('257.1.1.1') is False
    assert is_valid_ipv4_address('saddas') is False
    assert is_valid_ipv4_address('0:0:0:0:0:0:0:0') is False
