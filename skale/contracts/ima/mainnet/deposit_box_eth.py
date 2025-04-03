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


class DepositBoxEth(BaseContract):
    @transaction_method
    def deposit(self, schain_name: SchainName) -> TxRes:
        return self.contract.functions.deposit(schain_name)

    @transaction_method
    def deposit_direct(self, schain_name: SchainName, receiver: int) -> TxRes:
        return self.contract.functions.depositDirect(schain_name, receiver)

    @transaction_method
    def get_my_eth(self) -> TxRes:
        return self.contract.functions.getMyEth()

    @transaction_method
    def enable_active_eth_transfers(self, schain_name: SchainName) -> TxRes:
        return self.contract.functions.enableActiveEthTransfers(schain_name)

    def approve_transfers(self, address) -> int:
        return self.contract.functions.approveTransfers(address).call()

    def is_active_transfers(self, schain_name: SchainName) -> bool:
        keccak_hash = keccak.new(data=schain_name.encode('utf8'), digest_bits=256)
        hash = keccak_hash.digest()
        return self.contract.functions.activeEthTransfers(hash).call()

    @transaction_method
    def disable_active_eth_transfers(self, schain_name: SchainName) -> TxRes:
        return self.contract.functions.disableActiveEthTransfers(schain_name)

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.grantRole(role, address)
