#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" SKALE chain test """

from skale.utils.constants import SchainType
from tests.constants import LIFETIME_SECONDS


def test_get_schain_price(skale):
    for schain_type in SchainType:
        schain_price = skale.schains.get_schain_price(schain_type,
                                                      LIFETIME_SECONDS)
        assert schain_price > 0
        assert type(schain_price) is int
