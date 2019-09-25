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
""" SKALE config test """

import pytest
from web3.auto import w3

from skale import Skale
from skale.utils.account_tools import init_test_wallet
from tests.constants import ENDPOINT, TEST_ABI_FILEPATH
from tests.prepare_data import create_nodes, create_schain, cleanup_nodes_schain


@pytest.fixture
def skale():
    '''Returns a SKALE instance with provider from config'''
    return Skale(ENDPOINT, TEST_ABI_FILEPATH)


@pytest.fixture
def wallet():
    return init_test_wallet()


@pytest.fixture(scope='module')
def skale_wallet_with_nodes_schain():
    '''Init skale and wallet with two nodes and schain between them'''
    skale = Skale(ENDPOINT, TEST_ABI_FILEPATH)
    wallet = init_test_wallet()
    create_nodes(skale, wallet)
    create_schain(skale, wallet)
    yield skale, wallet
    cleanup_nodes_schain(skale, wallet)


@pytest.fixture
def empty_wallet():
    return w3.eth.account.create()
