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


from typing import List, Tuple

from eth_typing import ChecksumAddress
from multisigwallet_predeployed import MULTISIGWALLET_ADDRESS, MultiSigWalletGenerator
from web3 import Web3
from web3.contract.contract import ContractFunction

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.wallets import BaseWallet


class MultiSigContract(BaseContract):
    def __init__(
        self,
        web3: Web3,
        wallet: BaseWallet | None = None,
    ):
        multisigwallet_generator = MultiSigWalletGenerator()
        abi = multisigwallet_generator.get_abi()
        multisig_address = Web3.to_checksum_address(MULTISIGWALLET_ADDRESS)
        super().__init__(web3, multisig_address, abi, wallet)

    def confirmations(self, transaction_id: int, owner_address: ChecksumAddress) -> bool:
        return self.contract.functions.confirmations(transaction_id, owner_address).call()

    def get_confirmation_count(self, transaction_id: int) -> int:
        return self.contract.functions.getConfirmationCount(transaction_id).call()

    def get_confirmations(self, transaction_id: int) -> List[ChecksumAddress]:
        return self.contract.functions.getConfirmations(transaction_id).call()

    def get_owners(self) -> List[ChecksumAddress]:
        return self.contract.functions.getOwners().call()

    def get_transaction_count(self, pending: bool, executed: bool) -> int:
        return self.contract.functions.getTransactionCount(pending, executed).call()

    def get_transaction_ids(
            self,
            from_tx: int,
            to_tx: int,
            pending: bool,
            executed: bool
    ) -> List[int]:
        return self.contract.functions.getTransactionIds(
            from_tx,
            to_tx,
            pending,
            executed
        ).call()

    def is_corfirmed(self, transaction_id: int) -> bool:
        return self.contract.functions.isConfirmed(transaction_id).call()

    def is_owner(self, address: ChecksumAddress) -> bool:
        return self.contract.functions.isOwner(address).call()

    def owners(self, index: int) -> ChecksumAddress:
        return self.contract.functions.owners(index).call()

    def required(self) -> int:
        return self.contract.functions.required().call()

    def transaction_count(self) -> int:
        return self.contract.functions.transactionCount().call()

    def transactions(self, index: int) -> Tuple[ChecksumAddress, int, bytes, bool]:
        return self.contract.functions.transactions(index).call()

    @transaction_method
    def add_owner(self, owner: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.addOwner(owner)

    @transaction_method
    def change_requirement(self, required: int) -> ContractFunction:
        return self.contract.functions.changeRequirement(required)

    @transaction_method
    def confirm_transaction(self, transaction_id: int) -> ContractFunction:
        return self.contract.functions.confirmTransaction(transaction_id)

    @transaction_method
    def execute_transaction(self, transaction_id: int) -> ContractFunction:
        return self.contract.functions.executeTransaction(transaction_id)

    @transaction_method
    def remove_owner(self, owner: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.removeOwner(owner)

    @transaction_method
    def replace_owner(
        self,
        owner: ChecksumAddress,
        new_owner: ChecksumAddress,
    ) -> ContractFunction:
        return self.contract.functions.replaceOwner(owner, new_owner)

    @transaction_method
    def revoke_confirmation(self, transaction_id: int) -> ContractFunction:
        return self.contract.functions.revokeConfirmation(transaction_id)

    @transaction_method
    def submit_transaction(
        self,
        destination: ChecksumAddress,
        value: int,
        data: bytes,
    ) -> ContractFunction:
        return self.contract.functions.submitTransaction(
            destination,
            value,
            data,
        )
