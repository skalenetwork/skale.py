#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
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


def test_get_balance(skale, empty_account):
    empty_balance = skale.token.get_balance(empty_account.address)
    not_empty_balance = skale.token.get_balance(skale.wallet.address)

    assert empty_balance == 0
    assert not_empty_balance != 0
