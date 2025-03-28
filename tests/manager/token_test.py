"""SKALE token test"""

from tests.constants import TOKEN_TRANSFER_VALUE


def test_transfer(skale, empty_account):
    receiver_balance = skale.token.get_balance(empty_account.address)
    sender_balance = skale.token.get_balance(skale.wallet.address)

    assert receiver_balance == 0
    assert sender_balance != 0

    tx_res = skale.token.transfer(empty_account.address, TOKEN_TRANSFER_VALUE, wait_for=True)
    assert tx_res.receipt['status'] == 1

    receiver_balance_after = skale.token.get_balance(empty_account.address)
    sender_balance_after = skale.token.get_balance(skale.wallet.address)

    assert receiver_balance_after == TOKEN_TRANSFER_VALUE
    assert sender_balance_after == sender_balance - TOKEN_TRANSFER_VALUE


def test_transfer_wait_for(skale, empty_account):
    receiver_balance = skale.token.get_balance(empty_account.address)
    sender_balance = skale.token.get_balance(skale.wallet.address)

    assert receiver_balance == 0
    assert sender_balance != 0

    tx_res = skale.token.transfer(empty_account.address, TOKEN_TRANSFER_VALUE, wait_for=True)

    assert tx_res.receipt['status'] == 1

    receiver_balance_after = skale.token.get_balance(empty_account.address)
    sender_balance_after = skale.token.get_balance(skale.wallet.address)

    assert receiver_balance_after == TOKEN_TRANSFER_VALUE
    assert sender_balance_after == sender_balance - TOKEN_TRANSFER_VALUE


def test_get_balance(skale, empty_account):
    empty_balance = skale.token.get_balance(empty_account.address)
    not_empty_balance = skale.token.get_balance(skale.wallet.address)

    assert empty_balance == 0
    assert not_empty_balance != 0


def test_get_and_update_slashed_amount(skale):
    res = skale.token.get_and_update_slashed_amount(skale.wallet.address)
    assert res == 0
