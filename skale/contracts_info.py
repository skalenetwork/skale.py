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

import skale.contracts as contracts
from skale.utils.contract_info import ContractInfo
from skale.utils.contract_types import ContractTypes

CONTRACTS_INFO = [
    ContractInfo('contract_manager', 'ContractManager',
                 contracts.ContractManager, ContractTypes.API, False),
    ContractInfo('token', 'SkaleToken', contracts.Token, ContractTypes.API,
                 False),
    ContractInfo('manager', 'SkaleManager', contracts.Manager,
                 ContractTypes.API, True),
    ContractInfo('constants', 'Constants', contracts.Constants,
                 ContractTypes.INTERNAL, True),
    ContractInfo('nodes', 'NodesFunctionality', contracts.Nodes,
                 ContractTypes.API, True),
    ContractInfo('schains', 'SchainsFunctionality', contracts.SChains,
                 ContractTypes.API, True),
    ContractInfo('validators', 'ValidatorsFunctionality', contracts.Validators,
                 ContractTypes.API, True),
    ContractInfo('nodes_data', 'NodesData', contracts.NodesData,
                 ContractTypes.DATA, True),
    ContractInfo('schains_data', 'SchainsData', contracts.SChainsData,
                 ContractTypes.DATA, True),
    ContractInfo('validators_data', 'ValidatorsData', contracts.ValidatorsData,
                 ContractTypes.DATA, True),
    ContractInfo('dkg', 'SkaleDKG', contracts.DKG, ContractTypes.API, True),
]
