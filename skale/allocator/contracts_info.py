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

import skale.allocator.contracts as contracts
from skale.common_contracts.contract_manager import ContractManager
from skale.utils.contract_info import ContractInfo
from skale.utils.contract_types import ContractTypes


CONTRACTS_INFO = [
    ContractInfo('contract_manager', 'ContractManager',
                 ContractManager, ContractTypes.API, False),
    ContractInfo('core_escrow', 'CoreEscrow', contracts.CoreEscrow,
                 ContractTypes.API, True),
]


def get_contracts_info(contracts_data):
    contracts_info = {}
    for contract_info in contracts_data:
        contracts_info[contract_info.name] = contract_info
    return contracts_info


def get_base_contracts_info():
    return get_contracts_info(CONTRACTS_INFO)
