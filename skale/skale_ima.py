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
from typing import List

from skale.skale_base import SkaleBase
from skale.utils.contract_info import ContractInfo
from skale.utils.contract_types import ContractTypes
from skale.utils.helper import get_contracts_info


logger = logging.getLogger(__name__)


class SkaleIma(SkaleBase):
    @property
    def project_name(self) -> str:
        return 'mainnet-ima'

    def contracts_info(self) -> List[ContractInfo[SkaleIma]]:
        import skale.contracts.ima as contracts

        return [ContractInfo('linker', 'Linker', contracts.Linker, ContractTypes.API, False)]

    def set_contracts_info(self) -> None:
        self._SkaleBase__contracts_info = get_contracts_info(self.contracts_info())


def spawn_skale_ima_lib(skale_ima: SkaleIma) -> SkaleIma:
    """Clone skale ima object with the same wallet"""
    return SkaleIma(skale_ima._endpoint, skale_ima.instance.address, skale_ima.wallet)
