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

from skale_contracts.projects.skale_allocator import SkaleAllocatorContract
from skale_contracts.project_factory import SkaleProject

from skale.skale_base import SkaleBase
from skale.contracts.allocator.allocator import Allocator
from skale.contracts.allocator.escrow import Escrow


class SkaleAllocator(SkaleBase):
    """Represents skale-allocator smart contracts"""

    @property
    def project_name(self) -> SkaleProject:
        return SkaleProject.SKALE_ALLOCATOR

    @cached_property
    def allocator(self) -> Allocator:
        return Allocator(self, SkaleAllocatorContract.ALLOCATOR)

    @cached_property
    def escrow(self) -> Escrow:
        return Escrow(self, SkaleAllocatorContract.ESCROW)


def spawn_skale_allocator_lib(skale: SkaleAllocator) -> SkaleAllocator:
    return SkaleAllocator(skale._endpoint, skale.instance.address, skale.wallet)
