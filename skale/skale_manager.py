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
    from skale.contracts.manager import BountyV2
    from skale.contracts.manager import ConstantsHolder
    from skale.contracts.manager import ContractManager
    from skale.contracts.manager import DelegationController
    from skale.contracts.manager import DelegationPeriodManager
    from skale.contracts.manager import Distributor
    from skale.contracts.manager import DKG
    from skale.contracts.manager import KeyStorage
    from skale.contracts.manager import Manager
    from skale.contracts.manager import NodeRotation
    from skale.contracts.manager import Nodes
    from skale.contracts.manager import Punisher
    from skale.contracts.manager import SChains
    from skale.contracts.manager import SChainsInternal
    from skale.contracts.manager import SlashingTable
    from skale.contracts.manager import SyncManager
    from skale.contracts.manager import TimeHelpersWithDebug
    from skale.contracts.manager import Token
    from skale.contracts.manager import TokenState
    from skale.contracts.manager import ValidatorService
    from skale.contracts.manager import Wallets


logger = logging.getLogger(__name__)


class SkaleManager(SkaleBase):
    """Represents skale-manager smart contracts"""
    @property
    def project_name(self) -> str:
        return 'skale-manager'

    @staticmethod
    def contracts_info() -> List[ContractInfo[SkaleManager]]:
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
    def bounty_v2(self) -> BountyV2:
        return cast('BountyV2', self._get_contract('bounty_v2'))

    @property
    def constants_holder(self) -> ConstantsHolder:
        return cast('ConstantsHolder', self._get_contract('constants_holder'))

    @property
    def contract_manager(self) -> ContractManager:
        return cast('ContractManager', self._get_contract('contract_manager'))

    @property
    def delegation_controller(self) -> DelegationController:
        return cast('DelegationController', self._get_contract('delegation_controller'))

    @property
    def delegation_period_manager(self) -> DelegationPeriodManager:
        return cast('DelegationPeriodManager', self._get_contract('delegation_period_manager'))

    @property
    def distributor(self) -> Distributor:
        return cast('Distributor', self._get_contract('distributor'))

    @property
    def dkg(self) -> DKG:
        return cast('DKG', self._get_contract('dkg'))

    @property
    def key_storage(self) -> KeyStorage:
        return cast('KeyStorage', self._get_contract('key_storage'))

    @property
    def manager(self) -> Manager:
        return cast('Manager', self._get_contract('manager'))

    @property
    def node_rotation(self) -> NodeRotation:
        return cast('NodeRotation', self._get_contract('node_rotation'))

    @property
    def nodes(self) -> Nodes:
        return cast('Nodes', self._get_contract('nodes'))

    @property
    def punisher(self) -> Punisher:
        return cast('Punisher', self._get_contract('punisher'))

    @property
    def schains(self) -> SChains:
        return cast('SChains', self._get_contract('schains'))

    @property
    def schains_internal(self) -> SChainsInternal:
        return cast('SChainsInternal', self._get_contract('schains_internal'))

    @property
    def slashing_table(self) -> SlashingTable:
        return cast('SlashingTable', self._get_contract('slashing_table'))

    @property
    def sync_manager(self) -> SyncManager:
        return cast('SyncManager', self._get_contract('sync_manager'))

    @property
    def time_helpers_with_debug(self) -> TimeHelpersWithDebug:
        return cast('TimeHelpersWithDebug', self._get_contract('time_helpers_with_debug'))

    @property
    def token(self) -> Token:
        return cast('Token', self._get_contract('token'))

    @property
    def token_state(self) -> TokenState:
        return cast('TokenState', self._get_contract('token_state'))

    @property
    def validator_service(self) -> ValidatorService:
        return cast('ValidatorService', self._get_contract('validator_service'))

    @property
    def wallets(self) -> Wallets:
        return cast('Wallets', self._get_contract('wallets'))

    def init_contract_manager(self) -> None:
        from skale.contracts.manager.contract_manager import ContractManager
        self.add_lib_contract('contract_manager', ContractManager, 'ContractManager')

    def set_contracts_info(self) -> None:
        self.init_contract_manager()
        self._SkaleBase__contracts_info = get_contracts_info(self.contracts_info())


def spawn_skale_manager_lib(skale: SkaleManager) -> SkaleManager:
    """ Clone skale manager object with the same wallet """
    return SkaleManager(skale._endpoint, skale.instance.address, skale.wallet)
