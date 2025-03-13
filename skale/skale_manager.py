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
    import skale.contracts.manager as contracts


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
            ContractInfo(
                'contract_manager',
                'ContractManager',
                contracts.ContractManager,
                ContractTypes.API,
                False,
            ),
            ContractInfo('token', 'SkaleToken', contracts.Token, ContractTypes.API, False),
            ContractInfo('manager', 'SkaleManager', contracts.Manager, ContractTypes.API, True),
            ContractInfo(
                'constants_holder',
                'ConstantsHolder',
                contracts.ConstantsHolder,
                ContractTypes.INTERNAL,
                True,
            ),
            ContractInfo('nodes', 'Nodes', contracts.Nodes, ContractTypes.API, True),
            ContractInfo(
                'node_rotation', 'NodeRotation', contracts.NodeRotation, ContractTypes.API, True
            ),
            ContractInfo('schains', 'Schains', contracts.SChains, ContractTypes.API, True),
            ContractInfo(
                'schains_internal',
                'SchainsInternal',
                contracts.SChainsInternal,
                ContractTypes.API,
                True,
            ),
            ContractInfo('dkg', 'SkaleDKG', contracts.DKG, ContractTypes.API, True),
            ContractInfo(
                'key_storage', 'KeyStorage', contracts.KeyStorage, ContractTypes.API, True
            ),
            ContractInfo(
                'delegation_controller',
                'DelegationController',
                contracts.DelegationController,
                ContractTypes.API,
                False,
            ),
            ContractInfo(
                'delegation_period_manager',
                'DelegationPeriodManager',
                contracts.DelegationPeriodManager,
                ContractTypes.API,
                False,
            ),
            ContractInfo(
                'validator_service',
                'ValidatorService',
                contracts.ValidatorService,
                ContractTypes.API,
                False,
            ),
            ContractInfo(
                'token_state', 'TokenState', contracts.TokenState, ContractTypes.API, False
            ),
            ContractInfo(
                'distributor', 'Distributor', contracts.Distributor, ContractTypes.API, False
            ),
            ContractInfo(
                'slashing_table', 'SlashingTable', contracts.SlashingTable, ContractTypes.API, False
            ),
            ContractInfo('wallets', 'Wallets', contracts.Wallets, ContractTypes.API, True),
            ContractInfo('bounty_v2', 'BountyV2', contracts.BountyV2, ContractTypes.API, True),
            ContractInfo('punisher', 'Punisher', contracts.Punisher, ContractTypes.API, True),
            ContractInfo(
                'sync_manager', 'SyncManager', contracts.SyncManager, ContractTypes.API, False
            ),
            ContractInfo(
                'time_helpers_with_debug',
                'TimeHelpersWithDebug',
                contracts.TimeHelpersWithDebug,
                ContractTypes.API,
                False,
            ),
        ]

    @property
    def bounty_v2(self) -> contracts.BountyV2:
        return cast('contracts.BountyV2', self._get_contract('bounty_v2'))

    @property
    def constants_holder(self) -> contracts.ConstantsHolder:
        return cast('contracts.ConstantsHolder', self._get_contract('constants_holder'))

    @property
    def contract_manager(self) -> contracts.ContractManager:
        return cast('contracts.ContractManager', self._get_contract('contract_manager'))

    @property
    def delegation_controller(self) -> contracts.DelegationController:
        return cast('contracts.DelegationController', self._get_contract('delegation_controller'))

    @property
    def delegation_period_manager(self) -> contracts.DelegationPeriodManager:
        return cast(
            'contracts.DelegationPeriodManager', self._get_contract('delegation_period_manager')
        )

    @property
    def distributor(self) -> contracts.Distributor:
        return cast('contracts.Distributor', self._get_contract('distributor'))

    @property
    def dkg(self) -> contracts.DKG:
        return cast('contracts.DKG', self._get_contract('dkg'))

    @property
    def key_storage(self) -> contracts.KeyStorage:
        return cast('contracts.KeyStorage', self._get_contract('key_storage'))

    @property
    def manager(self) -> contracts.Manager:
        return cast('contracts.Manager', self._get_contract('manager'))

    @property
    def node_rotation(self) -> contracts.NodeRotation:
        return cast('contracts.NodeRotation', self._get_contract('node_rotation'))

    @property
    def nodes(self) -> contracts.Nodes:
        return cast('contracts.Nodes', self._get_contract('nodes'))

    @property
    def punisher(self) -> contracts.Punisher:
        return cast('contracts.Punisher', self._get_contract('punisher'))

    @property
    def schains(self) -> contracts.SChains:
        return cast('contracts.SChains', self._get_contract('schains'))

    @property
    def schains_internal(self) -> contracts.SChainsInternal:
        return cast('contracts.SChainsInternal', self._get_contract('schains_internal'))

    @property
    def slashing_table(self) -> contracts.SlashingTable:
        return cast('contracts.SlashingTable', self._get_contract('slashing_table'))

    @property
    def sync_manager(self) -> contracts.SyncManager:
        return cast('contracts.SyncManager', self._get_contract('sync_manager'))

    @property
    def time_helpers_with_debug(self) -> contracts.TimeHelpersWithDebug:
        return cast('contracts.TimeHelpersWithDebug', self._get_contract('time_helpers_with_debug'))

    @property
    def token(self) -> contracts.Token:
        return cast('contracts.Token', self._get_contract('token'))

    @property
    def token_state(self) -> contracts.TokenState:
        return cast('contracts.TokenState', self._get_contract('token_state'))

    @property
    def validator_service(self) -> contracts.ValidatorService:
        return cast('contracts.ValidatorService', self._get_contract('validator_service'))

    @property
    def wallets(self) -> contracts.Wallets:
        return cast('contracts.Wallets', self._get_contract('wallets'))

    def init_contract_manager(self) -> None:
        from skale.contracts.manager.contract_manager import ContractManager

        self.add_lib_contract('contract_manager', ContractManager, 'ContractManager')

    def set_contracts_info(self) -> None:
        self.init_contract_manager()
        self._SkaleBase__contracts_info = get_contracts_info(self.contracts_info())


def spawn_skale_manager_lib(skale: SkaleManager) -> SkaleManager:
    """Clone skale manager object with the same wallet"""
    return SkaleManager(skale._endpoint, skale.instance.address, skale.wallet)
