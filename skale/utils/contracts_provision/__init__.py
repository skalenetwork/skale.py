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

from skale.contracts.allocator.allocator import TimeUnit

# manager test constants

DEFAULT_NODE_NAME = 'test_node'
SECOND_NODE_NAME = 'test_node_2'

DEFAULT_SCHAIN_NAME = 'test_schain'

DEFAULT_DOMAIN_NAME = 'skale.test'

INITIAL_DELEGATION_PERIOD = 2
D_VALIDATOR_ID = 1
D_VALIDATOR_NAME = 'test'
D_VALIDATOR_DESC = 'test'
D_VALIDATOR_FEE = 10
D_VALIDATOR_MIN_DEL = 1000000

D_DELEGATION_PERIOD = 2
D_STAKE_MULTIPLIER = 100
D_DELEGATION_INFO = 'test'

MONTH_IN_SECONDS = (60 * 60 * 24 * 31) + 100
FIRST_DELEGATION_MONTH = 1

# allocator test constants

TEST_VESTING_SLIFF = 6
TEST_TOTAL_VESTING_DURATION = 36
TEST_VESTING_INTERVAL_TIME_UNIT = TimeUnit.MONTH
TEST_VESTING_INTERVAL = 6
TEST_CAN_DELEGATE = True
TEST_IS_TERMINATABLE = True

TEST_START_MONTH = 8

WEI_MULTIPLIER = 10 ** 18

TEST_FULL_AMOUNT = 5000 * WEI_MULTIPLIER
TEST_LOCKUP_AMOUNT = 1000 * WEI_MULTIPLIER

POLL_INTERVAL = 2

TEST_SKALE_AMOUNT = 100000

D_PLAN_ID = 1
