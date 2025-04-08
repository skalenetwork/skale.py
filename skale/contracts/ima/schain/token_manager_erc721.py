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

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes
from Crypto.Hash import keccak
from eth_typing import ChecksumAddress
from skale.types.schain import SchainName


class TokenManagerERC721(BaseContract):
    def automatic_deploy(self) -> bool:
        return self.contract.functions.automaticDeploy().call()

    @transaction_method
    def enable_automatic_deploy(self) -> TxRes:
        return self.contract.functions.enableAutomaticDeploy()

    @transaction_method
    def add_erc721(self, schain_name: SchainName, token_mn: int, token_sc: int) -> TxRes:
        return self.contract.functions.addERC721TokenByOwner(schain_name, token_mn, token_sc)

    @transaction_method
    def transfer_to_schain_erc721(
        self, schain_name: SchainName, address: ChecksumAddress, token_id: int
    ) -> TxRes:
        """address - token address on origin chain"""
        return self.contract.functions.transferToSchainERC721(schain_name, address, token_id)

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
    def exit_to_main_erc721(self, address: ChecksumAddress, token_id: int) -> TxRes:
        return self.contract.functions.exitToMainERC721(address, token_id)

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.grantRole(role, address)

    def get_role_member(self, role: bytes, index: int) -> bytes:
        return self.contract.functions.getRoleMember(role, index).call()

    def get_clones_erc721(self, schain_name: SchainName, address: ChecksumAddress) -> int:
        keccak_hash = keccak.new(data=schain_name.encode('utf8'), digest_bits=256)
        hash = keccak_hash.digest()
        return self.contract.functions.clonesErc721(hash, address).call()
