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


class TokenManagerERC721WithMetadata(BaseTokenManager):
    @transaction_method
    def add_erc721(self, schain_name: SchainName, token_mn: int, token_sc: int) -> ContractFunction:
        return self.contract.functions.addERC721TokenByOwner(schain_name, token_mn, token_sc)

    @transaction_method
    def transfer_to_schain_erc721(
        self, schain_name: SchainName, address: ChecksumAddress, token_id: int
    ) -> ContractFunction:
        """address - token address on origin chain"""
        return self.contract.functions.transferToSchainERC721(schain_name, address, token_id)

    @transaction_method
    def exit_to_main_erc721(self, address: ChecksumAddress, token_id: int) -> ContractFunction:
        return self.contract.functions.exitToMainERC721(address, token_id)

    def get_clones_erc721(self, schain_name: SchainName, address: ChecksumAddress) -> int:
        return self.contract.functions.clonesErc721(
            schain_name_to_hash(schain_name), address
        ).call()
