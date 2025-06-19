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

from Crypto.Hash import keccak
from eth_typing import ChecksumAddress

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes
from skale.types.schain import SchainName


class TokenManagerERC1155(BaseContract):
    @transaction_method
    def add_erc1155_token(self, schain_name: SchainName, token_mn: int, token_sc: int) -> TxRes:
        return self.contract.functions.addERC1155TokenByOwner(schain_name, token_mn, token_sc)

    @transaction_method
    def exit_to_main_erc1155(
        self, token_address: ChecksumAddress, token_id: int, amount: int
    ) -> TxRes:
        return self.contract.functions.exitToMainERC1155(token_address, token_id, amount)

    @transaction_method
    def exit_to_main_erc1155_batch(self, token_addres: int, token_ids: list, amount: list) -> TxRes:
        return self.contract.functions.exitToMainERC1155Batch(token_addres, token_ids, amount)

    @transaction_method
    def transfer_to_schain_erc1155(
        self, schain_name: SchainName, token_address: ChecksumAddress, token_id: int, amount: int
    ) -> TxRes:
        """
        schain_name - destination chain
        token address - address on source chain
        """
        return self.contract.functions.transferToSchainERC1155(
            schain_name, token_address, token_id, amount
        )

    @transaction_method
    def transfer_to_schain_erc1155_batch(
        self, schain_name: SchainName, token_address: ChecksumAddress, token_ids: list, amount: list
    ) -> TxRes:
        return self.contract.functions.transferToSchainERC1155Batch(
            schain_name, token_address, token_ids, amount
        )

    def get_clones_erc1155(self, schain_name: SchainName, address: ChecksumAddress) -> int:
        keccak_hash = keccak.new(data=schain_name.encode('utf8'), digest_bits=256)
        hash = keccak_hash.digest()
        return self.contract.functions.clonesErc1155(hash, address).call()

    def enable_automatic_deploy(self) -> TxRes:
        return self.contract.functions.enableAutomaticDeploy()

    @transaction_method
    def disable_automatic_deploy(self) -> TxRes:
        return self.contract.functions.disableAutomaticDeploy()

    def automatic_deploy_role(self) -> bytes:
        return self.contract.functions.AUTOMATIC_DEPLOY_ROLE().call()

    def token_registrar_role(self) -> bytes:
        return self.contract.functions.TOKEN_REGISTRAR_ROLE().call()

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return self.contract.functions.hasRole(role, address).call()

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.grantRole(role, address)

    def get_role_member(self, role: bytes, index: int) -> bytes:
        return self.contract.functions.getRoleMember(role, index).call()
