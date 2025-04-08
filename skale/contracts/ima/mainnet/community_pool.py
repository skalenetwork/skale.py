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

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes
from eth_typing import ChecksumAddress
from skale.types.schain import SchainName


class CommunityPool(BaseContract):
    @transaction_method
    def recharge_user_wallet(self, schain_name: SchainName, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.rechargeUserWallet(schain_name, address)

    @transaction_method
    def withdraw_funds(self, schain_name: SchainName, amount: int) -> TxRes:
        return self.contract.functions.withdrawFunds(schain_name, amount)

    @transaction_method
    def set_min_transaction_gas(self, min_gas_value: int) -> TxRes:
        return self.contract.functions.setMinTransactionGas(min_gas_value)

    @transaction_method
    def set_multiplier(self, new_numerator: int, new_divider: int) -> TxRes:
        return self.contract.functions.setMultiplier(new_numerator, new_divider)

    def get_balance(self, address: ChecksumAddress, schain_name: SchainName) -> int:
        return self.contract.functions.getBalance(address, schain_name).call()

    def check_user_balance(self, schain_name: SchainName, receiver: int) -> bool:
        keccak_hash = keccak.new(data=schain_name.encode('utf8'), digest_bits=256)
        schain_id = keccak_hash.digest()
        return self.contract.functions.checkUserBalance(schain_id, receiver).call()

    def get_recommended_recharge_amount(self, schain_name: SchainName, receiver: int) -> int:
        keccak_hash = keccak.new(data=schain_name.encode('utf8'), digest_bits=256)
        schain_id = keccak_hash.digest()
        return self.contract.functions.getRecommendedRechargeAmount(schain_id, receiver).call()

    def constant_setter_role(self) -> bool:
        return self.contract.functions.CONSTANT_SETTER_ROLE().call()

    def admin_role(self) -> bytes:
        return self.contract.functions.DEFAULT_ADMIN_ROLE().call()

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return self.contract.functions.hasRole(role, address).call()

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.grantRole(role, address)

    def get_role_member(self, role: bytes, index: int) -> bytes:
        return self.contract.functions.getRoleMember(role, index).call()
