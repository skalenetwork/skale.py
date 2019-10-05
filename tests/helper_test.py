import pytest

from skale.utils.helper import (
    await_receipt, check_receipt, format, get_nonce,
    generate_custom_config, is_valid_ipv4_address
)


def test_format():
    values = ['value1', 'value2']

    @format(['key1', 'key2'])
    def simple_function():
        return values

    assert simple_function() == {'key1': 'value1', 'key2': 'value2'}

    values = None

    assert simple_function() is None


def test_get_nonce(skale, wallet, empty_account):
    empty_nonce = get_nonce(skale, empty_account.address)
    assert empty_nonce == 0

    nonce = get_nonce(skale, wallet['address'])
    assert nonce != 0

    res = skale.token.transfer(empty_account.address, 5, wallet)
    reciept = await_receipt(skale.web3, res['tx'])
    check_receipt(reciept)

    new_nonce = get_nonce(skale, wallet['address'])
    assert new_nonce > nonce

    LIB_NONCE = 15
    skale.nonces[wallet['address']] = LIB_NONCE
    new_nonce = get_nonce(skale, wallet['address'])
    assert new_nonce == 2 * LIB_NONCE


def test_is_valid_ipv4_address():
    assert is_valid_ipv4_address('1.1.1.1') is True
    assert is_valid_ipv4_address('1.1.1') is False
    assert is_valid_ipv4_address('257.1.1.1') is False
    assert is_valid_ipv4_address('saddas') is False
    assert is_valid_ipv4_address('0:0:0:0:0:0:0:0') is False


def test_generate_custom_config():
    res = generate_custom_config('1.1.1.1', '1920')
    assert res == {'ip': '1.1.1.1', 'ws_port': '1920'}
    with pytest.raises(ValueError):
        generate_custom_config('', '')
