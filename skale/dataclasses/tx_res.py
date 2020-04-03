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


class TxRes():
    def __init__(self, tx_hash=None, data=None, receipt=None):
        self._hash = tx_hash
        self._data = data
        self._receipt = receipt

    @property
    def hash(self):
        return self._hash

    @property
    def data(self):
        return self._data

    @property
    def receipt(self):
        return self._receipt

    @receipt.setter
    def receipt(self, receipt: dict) -> None:
        self._receipt = receipt
