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

import skale.contracts.allocator as contracts
from skale.contracts.contract_manager import ContractManager
from skale.skale_base import SkaleBase
from skale.utils.contract_info import ContractInfo
from skale.utils.contract_types import ContractTypes
from skale.utils.helper import get_abi, get_contracts_info
from skale.wallets import BaseWallet


logger = logging.getLogger(__name__)


CONTRACTS_INFO = [
    ContractInfo('contract_manager', 'ContractManager',
                 ContractManager, ContractTypes.API, False),
    ContractInfo('escrow', 'Escrow', contracts.Escrow,
                 ContractTypes.API, True),
    ContractInfo('allocator', 'Allocator', contracts.Allocator,
                 ContractTypes.API, True)
]


class SkaleAllocator(SkaleBase):
    def init_contracts(self):
        abi = get_abi(self._abi_filepath)
        self.add_lib_contract('contract_manager', ContractManager, abi)
        self._SkaleBase__init_contracts_from_info(
            abi, get_contracts_info(CONTRACTS_INFO)
        )


def spawn_skale_allocator_from(skale,
                               wallet: BaseWallet = None,
                               provider_timeout: int = 30) -> SkaleAllocator:
    wallet = wallet or skale.wallet
    provider_timeout = provider_timeout or skale._provider_timeout
    return SkaleAllocator(skale._endpoint, skale._abi_filepath,
                          wallet, provider_timeout)
