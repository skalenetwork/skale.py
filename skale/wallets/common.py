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
from typing import Optional

from eth_account.datastructures import SignedMessage, SignedTransaction
from eth_typing import ChecksumAddress, HexStr
from web3 import Web3
from web3.types import _Hash32, TxParams, TxReceipt

from skale.transactions.exceptions import ChainIdError
from skale.utils.web3_utils import DEFAULT_BLOCKS_TO_WAIT


def ensure_chain_id(tx_dict: TxParams, web3: Web3) -> None:
    if not tx_dict.get('chainId'):
        tx_dict['chainId'] = web3.eth.chain_id
    if not tx_dict.get('chainId'):
        raise ChainIdError('chainId must be in tx_dict (see EIP-155)')


class MessageNotSignedError(Exception):
    """
    Raised when signing message failed
    """

    pass


class BaseWallet(ABC):
    @abstractmethod
    def sign(self, tx_dict: TxParams) -> SignedTransaction:
        pass

    @abstractmethod
    def sign_and_send(
        self,
        tx_dict: TxParams,
        multiplier: Optional[float] = None,
        priority: Optional[int] = None,
        method: Optional[str] = None,
    ) -> HexStr:
        pass

    @abstractmethod
    def sign_hash(self, unsigned_hash: str) -> SignedMessage:
        pass

    @property
    @abstractmethod
    def address(self) -> ChecksumAddress:
        pass

    @property
    @abstractmethod
    def public_key(self) -> str:
        pass

    @abstractmethod
    def wait(self, tx: _Hash32, confirmation_blocks: int = DEFAULT_BLOCKS_TO_WAIT) -> TxReceipt:
        pass
