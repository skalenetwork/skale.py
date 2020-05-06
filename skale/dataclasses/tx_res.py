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


class TransactionFailedError(Exception):
    pass


class TxRes:
    SUCCESS = 1
    NOT_PERFORMED = -1

    def __init__(self, tx_hash=None, dry_run_result=None, receipt=None):
        self._hash = tx_hash
        self._dry_run_result = dry_run_result
        self._receipt = receipt

    @property
    def dry_run_result(self):
        return self._dry_run_result

    @property
    def hash(self):
        return self._hash

    @property
    def receipt(self):
        return self._receipt

    @dry_run_result.setter
    def dry_run_result(self, dry_run_result: dict) -> None:
        self._dry_run_result = dry_run_result

    @hash.setter
    def hash(self, tx_hash: str) -> None:
        self._hash = tx_hash

    @receipt.setter
    def receipt(self, receipt: dict) -> None:
        self._receipt = receipt

    def dry_run_finished(self) -> bool:
        return self.dry_run_result is not None

    def receipt_received(self) -> bool:
        return self.receipt is not None

    def dry_run_status(self) -> int:
        if self.dry_run_finished():
            return self.dry_run_result.get('status', TxRes.NOT_PERFORMED)
        return TxRes.NOT_PERFORMED

    def dry_run_passed(self) -> bool:
        return self.dry_run_status() == TxRes.SUCCESS

    def receipt_status(self) -> int:
        if self.receipt_received():
            return self.receipt.get('status', TxRes.NOT_PERFORMED)
        return TxRes.NOT_PERFORMED

    def tx_passed(self) -> bool:
        return self.receipt_status() == TxRes.SUCCESS

    def raise_for_status(self) -> None:
        if self.dry_run_finished() and self.dry_run_status() != TxRes.SUCCESS:
            raise TransactionFailedError(f'Dry run check failed with error: '
                                         f'{self.dry_run_result}')
        if self.receipt_received() and self.receipt_status() != TxRes.SUCCESS:
            raise TransactionFailedError(f'Transaction failed with receipt: '
                                         f'{self.receipt}')
