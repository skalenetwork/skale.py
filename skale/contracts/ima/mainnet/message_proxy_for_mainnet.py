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
from eth_typing import ChecksumAddress
from skale.types.schain import SchainName


class MessageProxyForMainnet(BaseContract):
    @transaction_method
    def register_extra_contract(
        self, schain_name: SchainName, contract_address: ChecksumAddress
    ) -> TxRes:
        return self.contract.functions.registerExtraContract(schain_name, contract_address)

    @transaction_method
    def remove_extra_contract(
        self, schain_name: SchainName, contract_address: ChecksumAddress
    ) -> TxRes:
        return self.contract.functions.removeExtraContract(schain_name, contract_address)

    @transaction_method
    def add_reimbursed_contract(
        self, schain_name: SchainName, contract_address: ChecksumAddress
    ) -> TxRes:
        return self.contract.functions.addReimbursedContract(schain_name, contract_address)

    @transaction_method
    def remove_reimbursed_contracts(
        self, schain_name: SchainName, contract_address: ChecksumAddress
    ) -> TxRes:
        return self.contract.functions.removeReimbursedContract(schain_name, contract_address)

    @transaction_method
    def pause(self, schain_name: SchainName) -> TxRes:
        return self.contract.functions.pause(schain_name)

    @transaction_method
    def resume(self, schain_name: SchainName) -> TxRes:
        return self.contract.functions.resume(schain_name)

    def is_connected_chain(self, schain_name: SchainName) -> bool:
        return self.contract.functions.isConnectedChain(schain_name)

    def is_reimbursed_contract(self, schain_name: SchainName) -> bool:
        return self.contract.functions.isReimbursedContract(schain_name)

    def is_paused(self, schian_name: str) -> bool:
        return self.contract.functions.isPaused(schian_name)

    def extra_contract_register_role(self) -> bytes:
        return self.contract.functions.EXTRA_CONTRACT_REGISTRAR_ROLE().call()

    def pausable_role(self) -> bytes:
        return self.contract.functions.PAUSABLE_ROLE().call()

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.grantRole(role, address)

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return self.contract.functions.hasRole(role, address).call()

    def get_role_member(self, role: bytes, index: int) -> bytes:
        return self.contract.functions.getRoleMember(role, index).call()
