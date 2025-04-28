#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2025-Present SKALE Labs
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

from skale.skale_base import SkaleBase
from skale_contracts.projects.mirage_manager import MirageManagerContract
from skale_contracts.project_factory import SkaleProject

from skale.contracts.mirage.nodes import Nodes
from skale.contracts.mirage.committee import Committee
from skale.contracts.mirage.dkg import DKG
from skale.contracts.mirage.access_manager import AccessManager
from skale.contracts.mirage.status import Status
from skale.contracts.mirage.staking import Staking


class MirageManager(SkaleBase):
    @property
    def project_name(self) -> SkaleProject:
        return SkaleProject.MIRAGE_MANAGER

    @cached_property
    def nodes(self) -> Nodes:
        return Nodes(self, MirageManagerContract.NODES)

    @cached_property
    def committee(self) -> Committee:
        return Committee(self, MirageManagerContract.COMMITTEE)

    @cached_property
    def dkg(self) -> DKG:
        return DKG(self, MirageManagerContract.DKG)

    @cached_property
    def access_manager(self) -> AccessManager:
        return AccessManager(self, MirageManagerContract.MIRAGE_ACCESS_MANAGER)

    @cached_property
    def status(self) -> Status:
        return Status(self, MirageManagerContract.STATUS)

    @cached_property
    def staking(self) -> Staking:
        return Staking(self, MirageManagerContract.STAKING)
