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

from skale.skale_base import SkaleBase
import skale.contracts.allocator as contracts
from skale.contracts.contract_manager import ContractManager
from skale.utils.contract_info import ContractInfo
from skale.utils.contract_types import ContractTypes
from skale.utils.helper import get_abi, get_contracts_info


logger = logging.getLogger(__name__)


CONTRACTS_INFO = [
    ContractInfo('contract_manager', 'ContractManager',
                 ContractManager, ContractTypes.API, False),
    ContractInfo('core_escrow', 'CoreEscrow', contracts.CoreEscrow,
                 ContractTypes.API, True),
]


def spawn_skale_allocator_lib(skale):
    return SkaleAllocator(skale._endpoint, skale._abi_filepath, skale.wallet)


class SkaleAllocator(SkaleBase):
    def init_contracts(self):
        abi = get_abi(self._abi_filepath)
        self.add_lib_contract('contract_manager', ContractManager, abi)
        self._SkaleBase__init_contracts_from_info(abi,  get_contracts_info(CONTRACTS_INFO))
