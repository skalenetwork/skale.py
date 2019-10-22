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
""" SKALE test constants """

import os
from decimal import Decimal

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

DEFAULT_NODE_NAME = 'test_node'
DEFAULT_NODE_ID = 0
DEFAULT_NODE_HASH = '23bdf46c41fa300e431425baff124dc31625b34ec09b829f61aa16ab0102ca8d'

TEST_CONTRACT_NAME = 'NodesFunctionality'
TEST_CONTRACT_NAME_HASH = 'f88bdb637038c4be9f72381c0db0b0d7b7f369cfdd49619ee7e48aa7940482b9'
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

TOKEN_TRANSFER_VALUE = 100
ETH_TRANSFER_VALUE = Decimal('0.05')

DEFAULT_SCHAIN_NAME = 'test_schain'
DEFAULT_SCHAIN_INDEX = 0
DEFAULT_SCHAIN_ID = '9ca5dee9297f25a2d182b4a437c9b57b15430750391861ca3ddf1a763ba285e0'

LIFETIME_YEARS = 1
LIFETIME_SECONDS = LIFETIME_YEARS * 366 * 86400

EMPTY_SCHAIN_ARR = ['', '0x0000000000000000000000000000000000000000', 0, 0, 0, 0, 0, 0]
EMPTY_ETH_ACCOUNT = '0x0000000000000000000000000000000000000001'

MIN_NODES_IN_SCHAIN = 2

N_TEST_WALLETS = 2

ENDPOINT = os.environ['ENDPOINT']
TEST_ABI_FILEPATH = os.path.join(DIR_PATH, os.pardir, 'test_abi.json')

# constants contract
NEW_REWARD_PERIOD = 500
NEW_DELTA_PERIOD = 400
