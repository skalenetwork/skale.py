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


class RPCWalletError(Exception):
    """Raised when remote wallet returned an error"""


class InvalidWalletError(Exception):
    """Raised when wrong wallet class passed"""


class EmptyWalletError(Exception):
    """Raised when wrong wallet class passed"""


class SChainNotFoundException(Exception):
    """Raised when requested sChain is not found"""


class IncompatibleAbiError(Exception):
    """Raised when required contract is not found in the ABI file"""
    def __init__(self, key):
        message = f'Required field was not found in the ABI file: {key}'
        super().__init__(message)


class InvalidNodeIdError(Exception):
    """Raised when wrong node id passed"""
