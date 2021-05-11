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
import skale.contracts.manager as contracts
from skale.contracts.contract_manager import ContractManager
from skale.utils.contract_info import ContractInfo
from skale.utils.contract_types import ContractTypes
from skale.utils.helper import get_abi, get_contracts_info


logger = logging.getLogger(__name__)


CONTRACTS_INFO = [
    ContractInfo('contract_manager', 'ContractManager',
                 ContractManager, ContractTypes.API, False),
    ContractInfo('token', 'SkaleToken', contracts.Token, ContractTypes.API,
                 False),
    ContractInfo('manager', 'SkaleManager', contracts.Manager,
                 ContractTypes.API, True),
    ContractInfo('constants_holder', 'ConstantsHolder', contracts.ConstantsHolder,
                 ContractTypes.INTERNAL, True),
    ContractInfo('nodes', 'Nodes', contracts.Nodes,
                 ContractTypes.API, True),
    ContractInfo('node_rotation', 'NodeRotation', contracts.NodeRotation,
                 ContractTypes.API, True),
    ContractInfo('schains', 'Schains', contracts.SChains,
                 ContractTypes.API, True),
    ContractInfo('schains_internal', 'SchainsInternal', contracts.SChainsInternal,
                 ContractTypes.API, True),
    ContractInfo('dkg', 'SkaleDKG', contracts.DKG, ContractTypes.API, True),
    ContractInfo('key_storage', 'KeyStorage', contracts.KeyStorage, ContractTypes.API, True),
    ContractInfo('delegation_controller', 'DelegationController', contracts.DelegationController,
                 ContractTypes.API, False),
    ContractInfo('delegation_period_manager', 'DelegationPeriodManager',
                 contracts.DelegationPeriodManager, ContractTypes.API, False),
    ContractInfo('validator_service', 'ValidatorService', contracts.ValidatorService,
                 ContractTypes.API, False),
    ContractInfo('token_state', 'TokenState', contracts.TokenState,
                 ContractTypes.API, False),
    ContractInfo('distributor', 'Distributor', contracts.Distributor,
                 ContractTypes.API, False),
    ContractInfo('slashing_table', 'Distributor', contracts.SlashingTable,
                 ContractTypes.API, False),
    ContractInfo('wallets', 'Wallets', contracts.Wallets,
                 ContractTypes.API, True),
]


DEBUG_CONTRACTS_INFO = [

    ContractInfo('time_helpers_with_debug', 'TimeHelpersWithDebug', contracts.TimeHelpersWithDebug,
                 ContractTypes.API, False)
]


def spawn_skale_manager_lib(skale):
    """ Clone skale manager object with the same wallet """
    return SkaleManager(skale._endpoint, skale._abi_filepath, skale.wallet)


class SkaleManager(SkaleBase):
    def set_contracts_info(self):
        self.init_contract_manager()
        abi = get_abi(self._abi_filepath)
        self._SkaleBase__contracts_info = get_contracts_info(CONTRACTS_INFO)
        if self._SkaleBase__is_debug_contracts(abi):
            logger.info('Debug contracts found in ABI file')
            self._SkaleBase__contracts_info.update(get_contracts_info(DEBUG_CONTRACTS_INFO))
