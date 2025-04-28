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

from time import sleep

from web3.contract.contract import ContractEvent
from web3.types import LogReceipt, Wei
from web3._utils.filters import LogFilter

from skale.skale_allocator import SkaleAllocator
from skale.skale_manager import SkaleManager
from skale.utils.account_tools import send_tokens
from skale.utils.contracts_provision import (
    TEST_SKALE_AMOUNT,
    TEST_VESTING_CLIFF,
    TEST_TOTAL_VESTING_DURATION,
    TEST_VESTING_INTERVAL_TIME_UNIT,
    TEST_VESTING_INTERVAL,
    TEST_CAN_DELEGATE,
    TEST_IS_TERMINATABLE,
    POLL_INTERVAL,
    TEST_START_MONTH,
    TEST_FULL_AMOUNT,
    TEST_LOCKUP_AMOUNT,
)
from skale.wallets.common import BaseWallet


def _catch_event(event_obj: ContractEvent) -> LogReceipt:
    event_filter: LogFilter = event_obj.create_filter(fromBlock=0, toBlock='latest')
    while True:
        for event in event_filter.get_all_entries():
            return event
        sleep(POLL_INTERVAL)


def transfer_tokens_to_allocator(
    skale_manager: SkaleManager, skale_allocator: SkaleAllocator, amount: Wei = TEST_SKALE_AMOUNT
) -> None:
    send_tokens(skale_manager, skale_allocator.allocator.address, amount)


def add_test_plan(skale_allocator: SkaleAllocator) -> int:
    skale_allocator.allocator.add_plan(
        vesting_cliff=TEST_VESTING_CLIFF,
        total_vesting_duration=TEST_TOTAL_VESTING_DURATION,
        vesting_interval_time_unit=TEST_VESTING_INTERVAL_TIME_UNIT,
        vesting_interval=TEST_VESTING_INTERVAL,
        can_delegate=TEST_CAN_DELEGATE,
        is_terminatable=TEST_IS_TERMINATABLE,
    )
    return len(skale_allocator.allocator.get_all_plans())


def connect_test_beneficiary(
    skale_allocator: SkaleAllocator, plan_id: int, wallet: BaseWallet
) -> None:
    skale_allocator.allocator.connect_beneficiary_to_plan(
        beneficiary_address=wallet.address,
        plan_id=plan_id,
        start_month=TEST_START_MONTH,
        full_amount=TEST_FULL_AMOUNT,
        lockup_amount=TEST_LOCKUP_AMOUNT,
    )
