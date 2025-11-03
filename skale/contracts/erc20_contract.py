#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2025-Present SKALE Labs
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


from time import sleep

from eth_typing import ChecksumAddress
from web3 import Web3
from web3.contract.contract import ContractFunction
from web3.types import Wei

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.wallets import BaseWallet

ERC20_ABI = [
    {
        'inputs': [],
        'name': 'name',
        'outputs': [{'name': '', 'type': 'string'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'symbol',
        'outputs': [{'name': '', 'type': 'string'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'decimals',
        'outputs': [{'name': '', 'type': 'uint8'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'totalSupply',
        'outputs': [{'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [{'name': 'account', 'type': 'address'}],
        'name': 'balanceOf',
        'outputs': [{'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [{'name': 'to', 'type': 'address'}, {'name': 'amount', 'type': 'uint256'}],
        'name': 'transfer',
        'outputs': [{'name': '', 'type': 'bool'}],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [{'name': 'owner', 'type': 'address'}, {'name': 'spender', 'type': 'address'}],
        'name': 'allowance',
        'outputs': [{'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [{'name': 'spender', 'type': 'address'}, {'name': 'amount', 'type': 'uint256'}],
        'name': 'approve',
        'outputs': [{'name': '', 'type': 'bool'}],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [
            {'name': 'from', 'type': 'address'},
            {'name': 'to', 'type': 'address'},
            {'name': 'amount', 'type': 'uint256'},
        ],
        'name': 'transferFrom',
        'outputs': [{'name': '', 'type': 'bool'}],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
]


class Erc20Contract(BaseContract):
    def __init__(
        self,
        web3: Web3,
        address: ChecksumAddress,
        wallet: BaseWallet | None = None,
    ):
        super().__init__(web3, address, ERC20_ABI, wallet)

    def balance_of(self, account: ChecksumAddress) -> Wei:
        return Wei(self.contract.functions.balanceOf(account).call())

    @transaction_method
    def transfer(self, to: ChecksumAddress, amount: Wei) -> ContractFunction:
        return self.contract.functions.transfer(to, amount)

    @transaction_method
    def approve(self, spender: ChecksumAddress, amount: Wei) -> ContractFunction:
        return self.contract.functions.approve(spender, amount)

    def wait_for_balance_change(
        self,
        address: ChecksumAddress,
        initial_balance: Wei,
        timeout: int = 120,
        poll_interval: int = 5,
        raise_on_timeout: bool = False,
    ) -> bool:
        iterations = timeout // poll_interval + 1
        for _ in range(iterations):
            current_balance = self.balance_of(address)
            if current_balance != initial_balance:
                return True
            sleep(poll_interval)

        if raise_on_timeout:
            raise TimeoutError(f'Balance did not change for {address} within {timeout} seconds')
        return False
