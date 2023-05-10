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

from skale.transactions.exceptions import (
    DryRunFailedError,
    RevertError,
    TransactionFailedError
)

SUCCESS_STATUS = 1


def is_success(result: dict) -> bool:
    return result.get('status') == SUCCESS_STATUS


def is_success_or_not_performed(result: dict) -> bool:
    return result is None or is_success(result)


def is_revert_error(result: dict) -> bool:
    return result and result.get('error', None) and 'reverted' in result['error'].lower()


class TxRes:
    def __init__(self, dry_run_result=None, tx_hash=None, receipt=None):
        self.dry_run_result = dry_run_result
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

    def tx_failed(self) -> bool:
        return not is_success_or_not_performed(self.receipt)

    def raise_for_status(self) -> None:
        if self.dry_run_failed():
            if is_revert_error(self.dry_run_result):
                raise RevertError(self.dry_run_result['error'])
            raise DryRunFailedError(f'Dry run check failed. '
                                    f'See result {self.dry_run_result}')
        if self.tx_failed():
            raise TransactionFailedError(f'Transaction failed. '
                                         f'See receipt {self.receipt}')
