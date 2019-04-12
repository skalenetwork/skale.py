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
""" SKALE contract manager test """

from tests.constants import TEST_CONTRACT_NAME, ZERO_ADDRESS, TEST_CONTRACT_NAME_HASH


def test_get_contract_address(skale):
    contract_address = skale.get_contract_address(TEST_CONTRACT_NAME)
    assert ZERO_ADDRESS != contract_address


def test_get_contract_hash_by_name(skale):
    contract_name_hash = skale.contract_manager.get_contract_hash_by_name(TEST_CONTRACT_NAME)
    assert TEST_CONTRACT_NAME_HASH == contract_name_hash
