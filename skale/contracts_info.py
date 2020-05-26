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
    ContractInfo('constants_holder', 'ConstantsHolder', contracts.ConstantsHolder,
                 ContractTypes.INTERNAL, True),
    ContractInfo('schains', 'SchainsFunctionality', contracts.SChains,
                 ContractTypes.API, True),
    ContractInfo('monitors', 'MonitorsFunctionality', contracts.MonitorsFunctionality,
                 ContractTypes.API, True),
    ContractInfo('nodes_data', 'Nodes', contracts.Nodes,
                 ContractTypes.DATA, True),
    ContractInfo('schains_data', 'SchainsData', contracts.SChainsData,
                 ContractTypes.DATA, True),
    ContractInfo('monitors_data', 'MonitorsData', contracts.MonitorsData,
                 ContractTypes.DATA, True),
    ContractInfo('dkg', 'SkaleDKG', contracts.DKG, ContractTypes.API, True),
    ContractInfo('delegation_controller', 'DelegationController', contracts.DelegationController,
                 ContractTypes.API, False),
    ContractInfo('validator_service', 'ValidatorService', contracts.ValidatorService,
                 ContractTypes.API, False),
    ContractInfo('token_state', 'TokenState', contracts.TokenState,
                 ContractTypes.API, False),
    ContractInfo('distributor', 'Distributor', contracts.Distributor,
                 ContractTypes.API, False),
    ContractInfo('slashing_table', 'Distributor', contracts.SlashingTable,
                 ContractTypes.API, False),
]


DEBUG_CONTRACTS_INFO = [

    ContractInfo('time_helpers_with_debug', 'TimeHelpersWithDebug', contracts.TimeHelpersWithDebug,
                 ContractTypes.API, False)
]


def get_contracts_info(contracts_data):
    contracts_info = {}
    for contract_info in contracts_data:
        contracts_info[contract_info.name] = contract_info
    return contracts_info


def get_base_contracts_info():
    return get_contracts_info(CONTRACTS_INFO)


def get_debug_contracts_info():
    return get_contracts_info(DEBUG_CONTRACTS_INFO)
