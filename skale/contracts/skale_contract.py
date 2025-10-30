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

import logging
from typing import TYPE_CHECKING, Generic, TypeVar

from skale_contracts.types import ContractName

from skale.contracts.base_contract import BaseContract
from skale.skale_base import SkaleBase
from skale.wallets import BaseWallet

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)


SkaleType = TypeVar('SkaleType', bound=SkaleBase)


class SkaleContract(BaseContract, Generic[SkaleType]):
    def __init__(self, skale: SkaleType, name: ContractName):
        self.skale = skale
        self.name = name
        self.web3 = skale.web3
        self.init_contract(contract_name=name)

    def init_contract(self, contract_name: ContractName) -> None:
        address = self.skale.instance.get_contract_address(contract_name)
        abi = self.skale.instance.abi[contract_name]
        self._init_contract(address, abi)

    @property
    def wallet(self) -> BaseWallet:
        return self.skale.wallet

    @wallet.setter
    def wallet(self, value: BaseWallet) -> None:
        self.skale.wallet = value
