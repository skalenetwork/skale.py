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
from skale.utils.helper import schain_name_to_hash


class DepositBoxERC20(BaseDepositBox):
    @transaction_method
    def add_erc20_token(
        self, schain_name: SchainName, address: ChecksumAddress
    ) -> ContractFunction:
        return self.contract.functions.addERC20TokenByOwner(schain_name, address)

    @transaction_method
    def deposit_erc20(
        self, schain_name: SchainName, address: ChecksumAddress, amount: int
    ) -> ContractFunction:
        return self.contract.functions.depositERC20(schain_name, address, amount)

    @transaction_method
    def deposit_erc20_direct(
        self, schain_name: SchainName, address: ChecksumAddress, amount: int, receiver: int
    ) -> ContractFunction:
        return self.contract.functions.depositERC20Direct(schain_name, address, amount, receiver)

    @transaction_method
    def set_big_transfer_value(
        self, schain_name: SchainName, token: int, value: int
    ) -> ContractFunction:
        return self.contract.functions.setBigTransferValue(schain_name, token, value)

    @transaction_method
    def set_big_transfer_delay(self, schain_name: SchainName, delay: int) -> ContractFunction:
        return self.contract.functions.setBigTransferDelay(schain_name, delay)

    @transaction_method
    def set_arbitrage_duration(self, schain_name: SchainName, delay: int) -> ContractFunction:
        return self.contract.functions.setArbitrageDuration(schain_name, delay)

    @transaction_method
    def trust_receiver(self, schain_name: SchainName, address: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.trustReceiver(schain_name, address)

    def is_receiver_trusted(self, schain_name: SchainName, address: ChecksumAddress) -> bool:
        return self.contract.functions.isReceiverTrusted(
            schain_name_to_hash(schain_name), address
        ).call()

    def arbiter_role(self) -> bytes:
        return self.contract.functions.ARBITER_ROLE().call()

    def is_token_added(self, schain_name: SchainName, erc20_on_mainnet: ChecksumAddress) -> bool:
        return self.contract.functions.getSchainToERC20(schain_name, erc20_on_mainnet).call()
