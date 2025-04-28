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

from web3.constants import CHECKSUM_ADDRESSS_ZERO
from skale_contracts.types import ContractName
from skale_contracts.projects.skale_allocator import SkaleAllocatorContract

from skale.contracts.base_contract import BaseContract


class AllocatorContract(BaseContract):
    def init_contract(self, contract_name: ContractName) -> None:
        if contract_name == SkaleAllocatorContract.ESCROW:
            self.address = CHECKSUM_ADDRESSS_ZERO
        else:
            self.address = self.skale.instance.get_contract_address(contract_name)
        self.contract = self.skale.web3.eth.contract(
            address=self.address,
            abi=self.skale.instance.abi[contract_name],
        )
