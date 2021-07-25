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
""" SKALE base contract class """

import logging
from functools import wraps

from web3 import Web3

import skale.config as config
from skale.transactions.result import (TxRes, check_balance_and_gas,
                                       is_success, is_success_or_not_performed)
from skale.transactions.tools import make_dry_run_call, post_transaction
from skale.utils.account_tools import account_eth_balance_wei
from skale.utils.web3_utils import (
    DEFAULT_BLOCKS_TO_WAIT,
    MAX_WAITING_TIME,
    wait_for_confirmation_blocks
)

from skale.utils.helper import to_camel_case


logger = logging.getLogger(__name__)


def execute_dry_run(skale, method, custom_gas_limit, value=0) -> tuple:
    dry_run_result = make_dry_run_call(skale, method, custom_gas_limit, value)
    estimated_gas_limit = None
    if is_success(dry_run_result):
        estimated_gas_limit = dry_run_result['payload']
    return dry_run_result, estimated_gas_limit


def transaction_method(transaction):
    @wraps(transaction)
    def wrapper(
        self,
        *args,
        wait_for=True,
        blocks_to_wait=DEFAULT_BLOCKS_TO_WAIT,
        timeout=MAX_WAITING_TIME,
        gas_limit=None,
        gas_price=None,
        nonce=None,
        value=0,
        dry_run_only=False,
        skip_dry_run=False,
        raise_for_status=True,
        multiplier=None,
        priority=None,
        confirmation_blocks=0,
        **kwargs
    ):
        method = transaction(self, *args, **kwargs)
        dry_run_result, tx, receipt = None, None, None

        # Make dry_run and estimate gas limit
        estimated_gas_limit = None
        if not skip_dry_run and not config.DISABLE_DRY_RUN:
            dry_run_result, estimated_gas_limit = execute_dry_run(
                self.skale, method, gas_limit, value
            )

        gas_limit = gas_limit or estimated_gas_limit or \
            config.DEFAULT_GAS_LIMIT

        # Check balance
        balance = account_eth_balance_wei(self.skale.web3,
                                          self.skale.wallet.address)
        gas_price = gas_price or config.DEFAULT_GAS_PRICE_WEI or \
            self.skale.gas_price
        balance_check_result = check_balance_and_gas(balance, gas_price,
                                                     gas_limit, value)
        rich_enough = is_success(balance_check_result)

        # Send transaction
        should_send_transaction = not dry_run_only and \
            is_success_or_not_performed(dry_run_result)

        if rich_enough and should_send_transaction:
            tx = post_transaction(
                self.skale.wallet, method, gas_limit,
                gas_price, nonce, value, multiplier, priority
            )
            if wait_for:
                receipt = self.skale.wallet.wait(tx)
            if confirmation_blocks:
                wait_for_confirmation_blocks(
                    self.skale.web3,
                    confirmation_blocks
                )

        tx_res = TxRes(dry_run_result, balance_check_result, tx, receipt)

        if raise_for_status:
            tx_res.raise_for_status()
        return tx_res

    return wrapper


class BaseContract:
    def __init__(self, skale, name, address, abi):
        self.skale = skale
        self.name = name
        self.address = Web3.toChecksumAddress(address)
        self.contract = skale.web3.eth.contract(address=self.address, abi=abi)

    def __getattr__(self, attr):
        """Fallback for contract calls"""
        logger.debug("Calling contract function: %s", attr)

        def wrapper(*args, **kw):
            logger.debug('called with %r and %r' % (args, kw))
            camel_case_fn_name = to_camel_case(attr)
            if hasattr(self.contract.functions, camel_case_fn_name):
                return getattr(self.contract.functions,
                               camel_case_fn_name)(*args, **kw).call()
            if hasattr(self.contract.functions, attr):
                return getattr(self.contract.functions,
                               attr)(*args, **kw).call()
            raise AttributeError(attr)
        return wrapper
