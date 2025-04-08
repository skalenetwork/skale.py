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

from eth_typing import ChecksumAddress
from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes
from skale.types.schain import SchainName


class DepositBoxERC721WithMetadata(BaseContract):
    @transaction_method
    def deposit_erc721(
        self, schain_name: SchainName, address: ChecksumAddress, tokenID: int
    ) -> TxRes:
        return self.contract.functions.depositERC721(schain_name, address, tokenID)

    @transaction_method
    def add_erc721_token(self, schain_name: SchainName, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.addERC721TokenByOwner(schain_name, address)

    @transaction_method
    def deposit_erc721_direct(
        self, schain_name: SchainName, address: ChecksumAddress, token_id: int, receiver: int
    ) -> TxRes:
        return self.contract.functions.depositERC721Direct(schain_name, address, token_id, receiver)

    def get_schain_to_erc721(self, schain_name: SchainName, token_address) -> int:
        return self.contract.functions.getSchainToERC721(schain_name, token_address)
