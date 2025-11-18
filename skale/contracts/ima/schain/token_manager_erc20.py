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
from skale.contracts.ima.schain.base_token_manager import BaseTokenManager
from skale.types.schain import SchainName
from skale.utils.helper import schain_name_to_hash


class TokenManagerERC20(BaseTokenManager):
    @transaction_method
    def exit_to_main_erc20(self, token_address: ChecksumAddress, amount: int) -> ContractFunction:
        return self.contract.functions.exitToMainERC20(token_address, amount)

    @transaction_method
    def transfer_to_schain_erc20(
        self, schain_name: SchainName, token_address: ChecksumAddress, amount: int
    ) -> ContractFunction:
        return self.contract.functions.transferToSchainERC20(schain_name, token_address, amount)

    @transaction_method
    def transfer_to_schain_erc20_direct(
        self, schain_name: SchainName, token_address: ChecksumAddress, amount: int, receiver=str
    ) -> ContractFunction:
        return self.contract.functions.transferToSchainERC20Direct(
            schain_name, token_address, amount, receiver
        )

    @transaction_method
    def transfer_to_schain_hash_erc20_direct(
        self, schain_hash: str, token_address: ChecksumAddress, amount: int, receiver=str
    ) -> ContractFunction:
        return self.contract.functions.transferToSchainHashERC20Direct(
            schain_hash, token_address, amount, receiver
        )

    @transaction_method
    def add_erc20_token(
        self,
        origin_chain_name: SchainName,
        origin_address: ChecksumAddress,
        clone_address: ChecksumAddress,
    ) -> ContractFunction:
        return self.contract.functions.addERC20TokenByOwner(
            origin_chain_name, origin_address, clone_address
        )

    def get_clone(self, schain_name: SchainName, origin_address: ChecksumAddress) -> int:
        return self.contract.functions.clonesErc20(
            schain_name_to_hash(schain_name), origin_address
        ).call()
