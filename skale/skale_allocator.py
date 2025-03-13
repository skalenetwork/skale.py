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
from typing import TYPE_CHECKING, List, cast
from web3.constants import CHECKSUM_ADDRESSS_ZERO

from skale.skale_base import SkaleBase
from skale.utils.contract_info import ContractInfo
from skale.utils.contract_types import ContractTypes
from skale.utils.helper import get_contracts_info

if TYPE_CHECKING:
    from eth_typing import ChecksumAddress
    from skale.contracts.allocator.allocator import Allocator


logger = logging.getLogger(__name__)


def spawn_skale_allocator_lib(skale: SkaleAllocator) -> SkaleAllocator:
    return SkaleAllocator(skale._endpoint, skale.instance.address, skale.wallet)


class SkaleAllocator(SkaleBase):
    """Represents skale-allocator smart contracts"""

    @property
    def project_name(self) -> str:
        return 'skale-allocator'

    @property
    def allocator(self) -> Allocator:
        return cast('Allocator', super()._get_contract('allocator'))

    def contracts_info(self) -> List[ContractInfo[SkaleAllocator]]:
        import skale.contracts.allocator as contracts

        return [
            ContractInfo('escrow', 'Escrow', contracts.Escrow, ContractTypes.API, True),
            ContractInfo('allocator', 'Allocator', contracts.Allocator, ContractTypes.API, True),
        ]

    def get_contract_address(self, name: str) -> ChecksumAddress:
        if name == 'Escrow':
            return CHECKSUM_ADDRESSS_ZERO
        return super().get_contract_address(name)

    def set_contracts_info(self) -> None:
        self._SkaleBase__contracts_info = get_contracts_info(self.contracts_info())
