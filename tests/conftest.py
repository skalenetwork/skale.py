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

from skale import BlockchainEnv, Skale
from skale.utils.account_tools import init_test_wallet
from tests.constants import RPC_IP, RPC_PORT


@pytest.fixture
def skale():
    '''Returns a SKALE instance with provider from config'''
    return Skale(BlockchainEnv.TEST, ip=RPC_IP, ws_port=RPC_PORT)


@pytest.fixture
def wallet():
    return init_test_wallet()


@pytest.fixture
def empty_wallet():
    return w3.eth.account.create()
