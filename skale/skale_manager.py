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

from __future__ import annotations
import logging
from typing import List, TYPE_CHECKING, cast

from skale.skale_base import SkaleBase
from skale.utils.contract_info import ContractInfo
from skale.utils.contract_types import ContractTypes
from skale.utils.helper import get_contracts_info

if TYPE_CHECKING:
    from skale.contracts.manager.node_rotation import NodeRotation
    from skale.contracts.manager.schains import SChains
    from skale.contracts.manager.schains_internal import SChainsInternal
    from skale.contracts.manager.token import Token


logger = logging.getLogger(__name__)


class SkaleManager(SkaleBase):
    """Represents skale-manager smart contracts"""
    @property
    def project_name(self) -> str:
        return 'skale-manager'

    def contracts_info(self) -> List[ContractInfo[SkaleManager]]:
        import skale.contracts.manager as contracts
        return [
            ContractInfo('contract_manager', 'ContractManager',
                         contracts.ContractManager, ContractTypes.API, False),
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
            ContractInfo('key_storage', 'KeyStorage',
                         contracts.KeyStorage, ContractTypes.API, True),
            ContractInfo('delegation_controller', 'DelegationController',
                         contracts.DelegationController, ContractTypes.API, False),
            ContractInfo('delegation_period_manager', 'DelegationPeriodManager',
                         contracts.DelegationPeriodManager, ContractTypes.API, False),
            ContractInfo('validator_service', 'ValidatorService',
                         contracts.ValidatorService, ContractTypes.API, False),
            ContractInfo('token_state', 'TokenState', contracts.TokenState,
                         ContractTypes.API, False),
            ContractInfo('distributor', 'Distributor', contracts.Distributor,
                         ContractTypes.API, False),
            ContractInfo('slashing_table', 'SlashingTable', contracts.SlashingTable,
                         ContractTypes.API, False),
            ContractInfo('wallets', 'Wallets', contracts.Wallets,
                         ContractTypes.API, True),
            ContractInfo('bounty_v2', 'BountyV2', contracts.BountyV2,
                         ContractTypes.API, True),
            ContractInfo('punisher', 'Punisher', contracts.Punisher,
                         ContractTypes.API, True),
            ContractInfo('sync_manager', 'SyncManager', contracts.SyncManager,
                         ContractTypes.API, False),
            ContractInfo('time_helpers_with_debug', 'TimeHelpersWithDebug',
                         contracts.TimeHelpersWithDebug, ContractTypes.API, False)
        ]

    @property
    def node_rotation(self) -> NodeRotation:
        return cast('NodeRotation', self._get_contract('node_rotation'))

    @property
    def schains(self) -> SChains:
        return cast('SChains', self._get_contract('schains'))

    @property
    def schains_internal(self) -> SChainsInternal:
        return cast('SChainsInternal', self._get_contract('schains_internal'))

    @property
    def token(self) -> Token:
        return cast('Token', self._get_contract('token'))

    def init_contract_manager(self) -> None:
        from skale.contracts.manager.contract_manager import ContractManager
        self.add_lib_contract('contract_manager', ContractManager, 'ContractManager')

    def set_contracts_info(self) -> None:
        self.init_contract_manager()
        self._SkaleBase__contracts_info = get_contracts_info(self.contracts_info())


def spawn_skale_manager_lib(skale: SkaleManager) -> SkaleManager:
    """ Clone skale manager object with the same wallet """
    return SkaleManager(skale._endpoint, skale.instance.address, skale.wallet)
