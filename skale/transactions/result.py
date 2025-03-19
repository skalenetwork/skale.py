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

import enum
from typing import Mapping, NamedTuple

from web3.types import TxReceipt
from eth_typing import HexStr

from skale.transactions.exceptions import (
    DryRunFailedError,
    DryRunRevertError,
    TransactionFailedError,
)


class TxStatus(int, enum.Enum):
    FAILED = 0
    SUCCESS = 1


class TxCallResult(NamedTuple):
    status: TxStatus
    error: str
    message: str
    data: Mapping[str, str | int]


class TxRes:
    def __init__(
        self,
        tx_call_result: TxCallResult | None = None,
        tx_hash: HexStr | None = None,
        receipt: TxReceipt | None = None,
    ):
        self.tx_call_result = tx_call_result
        self.tx_hash = tx_hash
        self.receipt = receipt
        self.attempts = 0

    def __str__(self) -> str:
        return (
            f'TxRes hash: {self.tx_hash}, tx_call_result {self.tx_call_result}, '
            f'receipt {self.receipt}'
        )

    def __repr__(self) -> str:
        return (
            f'TxRes hash: {self.tx_hash}, tx_call_result {self.tx_call_result}, '
            f'receipt {self.receipt}'
        )

    def raise_for_status(self) -> None:
        if self.receipt is not None:
            if self.receipt['status'] == TxStatus.FAILED:
                raise TransactionFailedError(
                    'Tx status is failed', {key: str(value) for key, value in self.receipt.items()}
                )
        elif self.tx_call_result is not None and self.tx_call_result.status == TxStatus.FAILED:
            if self.tx_call_result.error == 'revert':
                raise DryRunRevertError(self.tx_call_result.message)
            else:
                raise DryRunFailedError(self.tx_call_result.message)
