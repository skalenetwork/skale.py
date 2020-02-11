""" SKALE token test """

from skale.utils.web3_utils import wait_receipt

from tests.constants import TOKEN_TRANSFER_VALUE


def test_transfer(skale, empty_account):
    receiver_balance = skale.token.get_balance(empty_account.address)
    sender_balance = skale.token.get_balance(skale.wallet.address)

    assert receiver_balance == 0
    assert sender_balance != 0

    res = skale.token.transfer(empty_account.address, TOKEN_TRANSFER_VALUE)
    receipt = wait_receipt(skale.web3, res['tx'])

    assert receipt['status'] == 1

    receiver_balance_after = skale.token.get_balance(empty_account.address)
    sender_balance_after = skale.token.get_balance(skale.wallet.address)

    assert receiver_balance_after == TOKEN_TRANSFER_VALUE
    assert sender_balance_after == sender_balance - TOKEN_TRANSFER_VALUE


def test_transfer_wait_for(skale, empty_account):
    receiver_balance = skale.token.get_balance(empty_account.address)
    sender_balance = skale.token.get_balance(skale.wallet.address)

    assert receiver_balance == 0
    assert sender_balance != 0

    receipt = skale.token.transfer(empty_account.address, TOKEN_TRANSFER_VALUE,
                                   wait_for=True)

    assert receipt['status'] == 1

    receiver_balance_after = skale.token.get_balance(empty_account.address)
    sender_balance_after = skale.token.get_balance(skale.wallet.address)

    assert receiver_balance_after == TOKEN_TRANSFER_VALUE
    assert sender_balance_after == sender_balance - TOKEN_TRANSFER_VALUE


def test_get_balance(skale, empty_account):
    empty_balance = skale.token.get_balance(empty_account.address)
    not_empty_balance = skale.token.get_balance(skale.wallet.address)

    assert empty_balance == 0
    assert not_empty_balance != 0
