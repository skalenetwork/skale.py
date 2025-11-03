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
from web3.contract.contract import ContractFunction

from skale.contracts.base_contract import transaction_method
from skale.contracts.ima.mainnet.base_deposit_box import BaseDepositBox
from skale.types.schain import SchainName


class DepositBoxERC1155(BaseDepositBox):
    """Class deposit"""

    @transaction_method
    def add_erc1155_token(
        self, schain_name: SchainName, address: ChecksumAddress
    ) -> ContractFunction:
        return self.contract.functions.addERC1155TokenByOwner(schain_name, address)

    @transaction_method
    def deposit_erc1155(
        self, schain_name: SchainName, address: ChecksumAddress, token_id: int, amount: int
    ) -> ContractFunction:
        """Deposit ERC1155"""
        return self.contract.functions.depositERC1155(schain_name, address, token_id, amount)

    @transaction_method
    def deposit_direct_erc1155(
        self,
        schain_name: SchainName,
        address: ChecksumAddress,
        token_id: int,
        amount: int,
        receiver: int,
    ) -> ContractFunction:
        """Direct deposit ERC1155"""
        return self.contract.functions.depositERC1155Direct(
            schain_name, address, token_id, amount, receiver
        )

    @transaction_method
    def deposit_erc1155_batch(
        self, schain_name: SchainName, address: ChecksumAddress, ids: list, amount: list
    ) -> ContractFunction:
        return self.contract.functions.depositERC1155Batch(schain_name, address, ids, amount)

    def get_schain_to_erc1155(
        self, schain_name: SchainName, token_address: ChecksumAddress
    ) -> bool:
        return self.contract.functions.getSchainToERC1155(schain_name, token_address).call()
