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


class DepositBoxERC20(BaseContract):
    """Deposit Box"""

    def is_whitelisted(self, schain_name: SchainName) -> bool:
        return self.contract.functions.isWhitelisted(schain_name).call()

    @transaction_method
    def enable_whitelist(self, schain_name: SchainName) -> TxRes:
        return self.contract.functions.enableWhitelist(schain_name)

    @transaction_method
    def disable_whitelist(self, schain_name: SchainName) -> TxRes:
        return self.contract.functions.disableWhitelist(schain_name)

    @transaction_method
    def add_erc20_token(self, schain_name: SchainName, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.addERC20TokenByOwner(schain_name, address)

    @transaction_method
    def deposit_erc20(
        self, schain_name: SchainName, address: ChecksumAddress, amount: int
    ) -> TxRes:
        return self.contract.functions.depositERC20(schain_name, address, amount)

    @transaction_method
    def deposit_erc20_direct(
        self, schain_name: SchainName, address: ChecksumAddress, amount: int, receiver: int
    ) -> TxRes:
        return self.contract.functions.depositERC20Direct(schain_name, address, amount, receiver)

    @transaction_method
    def set_big_transfer_value(self, schain_name: SchainName, token: int, value: int) -> TxRes:
        return self.contract.functions.setBigTransferValue(schain_name, token, value)

    @transaction_method
    def set_big_transfer_delay(self, schain_name: SchainName, delay: int) -> TxRes:
        return self.contract.functions.setBigTransferDelay(schain_name, delay)

    @transaction_method
    def set_arbitrage_duration(self, schain_name: SchainName, delay: int) -> TxRes:
        return self.contract.functions.setArbitrageDuration(schain_name, delay)

    @transaction_method
    def trust_receiver(self, schain_name: SchainName, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.trustReceiver(schain_name, address)

    def is_receiver_trusted(self, schain_name: SchainName, address: ChecksumAddress) -> bool:
        keccak_hash = keccak.new(data=schain_name.encode('utf8'), digest_bits=256)
        schain_id = keccak_hash.digest()
        return self.contract.functions.isReceiverTrusted(schain_id, address).call()

    def arbiter_role(self) -> bytes:
        return self.contract.functions.ARBITER_ROLE().call()

    def admin_role(self) -> bytes:
        return self.contract.functions.DEFAULT_ADMIN_ROLE().call()

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return self.contract.functions.hasRole(role, address).call()

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.grantRole(role, address)

    def get_role_member(self, role: bytes, index: int) -> bytes:
        return self.contract.functions.getRoleMember(role, index).call()
