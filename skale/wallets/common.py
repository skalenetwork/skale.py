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

from abc import ABC, abstractmethod
from skale.utils.exceptions import ChainIdError


def ensure_chain_id(tx_dict, web3):
    if not tx_dict.get('chainId'):
        tx_dict['chainId'] = web3.eth.chainId
    if not tx_dict.get('chainId'):
        raise ChainIdError('chainId must be in tx_dict (see EIP-155)')


class BaseWallet(ABC):
    @abstractmethod
    def sign(self, tx):
        pass

    @abstractmethod
    def sign_and_send(self, tx_dict) -> str:
        pass

    @abstractmethod
    def sign_hash(self, unsigned_hash: str):
        pass

    @property
    @abstractmethod
    def address(self):
        pass

    @property
    @abstractmethod
    def public_key(self):
        pass
