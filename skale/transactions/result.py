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


SUCCESS_STATUS = 1


class TransactionError(Exception):
    pass


class DryRunFailedError(TransactionError):
    pass


class InsufficientBalanceError(TransactionError):
    pass


class TransactionFailedError(TransactionError):
    pass


def check_balance(balance: int, gas_price: int, gas_limit: int, value: int) -> dict:
    tx_cost = gas_price * gas_limit + value
    if balance < tx_cost:
        status = 0
        msg = f'Transaction requires {tx_cost}. Wallet has {balance} wei'
    else:
        status = 1
        msg = 'ok'
    return {'status': status, 'msg': msg}


def check_balance_and_gas(balance, gas_price, gas_limit, value):
    if gas_limit:
        return check_balance(balance, gas_price, gas_limit, value)
    return {'status': 0, 'msg': 'Gas limit is empty'}


def is_success(result: dict) -> bool:
    return result.get('status') == SUCCESS_STATUS


def is_success_or_not_performed(result: dict) -> bool:
    return result is None or is_success(result)


class TxRes:
    def __init__(self, dry_run_result=None, balance_check_result=None,
                 tx_hash=None, receipt=None):
        self.dry_run_result = dry_run_result
        self.balance_check_result = balance_check_result
        self.tx_hash = tx_hash
        self.receipt = receipt

    def __str__(self) -> str:
        return (
            f'TxRes hash: {self.tx_hash}, dry_run_result {self.dry_run_result}, '
            f'receipt {self.receipt}'
        )

    def __repr__(self) -> str:
        return (
            f'TxRes hash: {self.tx_hash}, dry_run_result {self.dry_run_result}, '
            f'receipt {self.receipt}'
        )

    def dry_run_failed(self) -> bool:
        return not is_success_or_not_performed(self.dry_run_result)

    def balance_check_failed(self) -> bool:
        return not is_success_or_not_performed(self.balance_check_result)

    def tx_failed(self) -> bool:
        return not is_success_or_not_performed(self.receipt)

    def raise_for_status(self) -> None:
        if self.dry_run_failed():
            raise DryRunFailedError(f'Dry run check failed. '
                                    f'See result {self.dry_run_result}')
        if self.balance_check_failed():
            raise InsufficientBalanceError(
                'Balance check failed. ',
                f'See result {self.balance_check_result}'
            )
        if self.tx_failed():
            raise TransactionFailedError(f'Transaction failed. '
                                         f'See receipt {self.receipt}')
