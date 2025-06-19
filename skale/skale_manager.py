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

from functools import cached_property

from skale_contracts.projects.skale_manager import SkaleManagerContract
from skale_contracts.project_factory import SkaleProject

from skale.skale_base import SkaleBase

from skale.contracts.manager.bounty_v2 import BountyV2
from skale.contracts.manager.constants_holder import ConstantsHolder
from skale.contracts.manager.contract_manager import ContractManager
from skale.contracts.manager.delegation.delegation_controller import DelegationController
from skale.contracts.manager.delegation.delegation_period_manager import DelegationPeriodManager
from skale.contracts.manager.delegation.distributor import Distributor
from skale.contracts.manager.delegation.slashing_table import SlashingTable
from skale.contracts.manager.delegation.token_state import TokenState
from skale.contracts.manager.delegation.validator_service import ValidatorService
from skale.contracts.manager.dkg import DKG
from skale.contracts.manager.key_storage import KeyStorage
from skale.contracts.manager.manager import Manager
from skale.contracts.manager.node_rotation import NodeRotation
from skale.contracts.manager.nodes import Nodes
from skale.contracts.manager.punisher import Punisher
from skale.contracts.manager.schains import SChains
from skale.contracts.manager.schains_internal import SChainsInternal
from skale.contracts.manager.sync_manager import SyncManager
from skale.contracts.manager.test.time_helpers_with_debug import TimeHelpersWithDebug
from skale.contracts.manager.token import Token
from skale.contracts.manager.wallets import Wallets


class SkaleManager(SkaleBase):
    """Represents skale-manager smart contracts"""

    @property
    def project_name(self) -> SkaleProject:
        return SkaleProject.SKALE_MANAGER

    @cached_property
    def contract_manager(self) -> ContractManager:
        return ContractManager(self, SkaleManagerContract.CONTRACT_MANAGER)

    @cached_property
    def token(self) -> Token:
        return Token(self, SkaleManagerContract.SKALE_TOKEN)

    @cached_property
    def manager(self) -> Manager:
        return Manager(self, SkaleManagerContract.SKALE_MANAGER)

    @cached_property
    def constants_holder(self) -> ConstantsHolder:
        return ConstantsHolder(self, SkaleManagerContract.CONSTANTS_HOLDER)

    @cached_property
    def nodes(self) -> Nodes:
        return Nodes(self, SkaleManagerContract.NODES)

    @cached_property
    def node_rotation(self) -> NodeRotation:
        return NodeRotation(self, SkaleManagerContract.NODE_ROTATION)

    @cached_property
    def schains(self) -> SChains:
        return SChains(self, SkaleManagerContract.SCHAINS)

    @cached_property
    def schains_internal(self) -> SChainsInternal:
        return SChainsInternal(self, SkaleManagerContract.SCHAINS_INTERNAL)

    @cached_property
    def dkg(self) -> DKG:
        return DKG(self, SkaleManagerContract.SKALE_DKG)

    @cached_property
    def key_storage(self) -> KeyStorage:
        return KeyStorage(self, SkaleManagerContract.KEY_STORAGE)

    @cached_property
    def delegation_controller(self) -> DelegationController:
        return DelegationController(self, SkaleManagerContract.DELEGATION_CONTROLLER)

    @cached_property
    def delegation_period_manager(self) -> DelegationPeriodManager:
        return DelegationPeriodManager(self, SkaleManagerContract.DELEGATION_PERIOD_MANAGER)

    @cached_property
    def validator_service(self) -> ValidatorService:
        return ValidatorService(self, SkaleManagerContract.VALIDATOR_SERVICE)

    @cached_property
    def token_state(self) -> TokenState:
        return TokenState(self, SkaleManagerContract.TOKEN_STATE)

    @cached_property
    def distributor(self) -> Distributor:
        return Distributor(self, SkaleManagerContract.DISTRIBUTOR)

    @cached_property
    def slashing_table(self) -> SlashingTable:
        return SlashingTable(self, SkaleManagerContract.SLASHING_TABLE)

    @cached_property
    def wallets(self) -> Wallets:
        return Wallets(self, SkaleManagerContract.WALLETS)

    @cached_property
    def bounty_v2(self) -> BountyV2:
        return BountyV2(self, SkaleManagerContract.BOUNTY_V2)

    @cached_property
    def punisher(self) -> Punisher:
        return Punisher(self, SkaleManagerContract.PUNISHER)

    @cached_property
    def sync_manager(self) -> SyncManager:
        return SyncManager(self, SkaleManagerContract.SYNC_MANAGER)

    @cached_property
    def time_helpers_with_debug(self) -> TimeHelpersWithDebug:
        return TimeHelpersWithDebug(self, SkaleManagerContract.TIME_HELPERS_WITH_DEBUG)


def spawn_skale_manager_lib(skale: SkaleManager) -> SkaleManager:
    return SkaleManager(skale._endpoint, skale.instance.address, skale.wallet)
