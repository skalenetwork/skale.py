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
"""SKALE Contract manager class"""

from Crypto.Hash import keccak
from eth_typing import ChecksumAddress
from web3 import Web3

from web3.contract.contract import ContractFunction
from skale.contracts.base_contract import transaction_method
from skale.contracts.skale_manager_contract import SkaleManagerContract
from skale.utils.helper import add_0x_prefix


class ContractManager(SkaleManagerContract):
    @transaction_method
    def set_contracts_address(
        self, contracts_name: str, contracts_address: ChecksumAddress
    ) -> 'ContractFunction':
        return self.contract.functions.setContractsAddress(contracts_name, contracts_address)

    def get_contract_address(self, name: str) -> ChecksumAddress:
        contract_hash = add_0x_prefix(self.get_contract_hash_by_name(name))
        return Web3.to_checksum_address(self.contract.functions.contracts(contract_hash).call())

    def get_contract_hash_by_name(self, name: str) -> str:
        keccak_hash = keccak.new(data=name.encode('utf8'), digest_bits=256)
        return keccak_hash.hexdigest()
