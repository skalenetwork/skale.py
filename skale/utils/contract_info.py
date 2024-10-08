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
""" Contract info utilities """

from __future__ import annotations
from typing import Generic, NamedTuple, Type, TYPE_CHECKING

from skale.contracts.base_contract import SkaleType

if TYPE_CHECKING:
    from skale.contracts.base_contract import BaseContract
    from skale.utils.contract_types import ContractTypes


class ContractInfo(NamedTuple, Generic[SkaleType]):
    name: str
    contract_name: str
    contract_class: Type[BaseContract[SkaleType]]
    type: ContractTypes
    upgradeable: bool
