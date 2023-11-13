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
from typing import Dict, Optional

from web3 import Web3

import skale.config as config
from skale.transactions.result import TxRes
from skale.transactions.tools import make_dry_run_call, transaction_from_method, TxStatus
from skale.utils.web3_utils import (
    DEFAULT_BLOCKS_TO_WAIT,
    get_eth_nonce,
    MAX_WAITING_TIME,
    wait_for_confirmation_blocks
)

from skale.utils.helper import to_camel_case


logger = logging.getLogger(__name__)


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
        max_fee_per_gas=None,
        max_priority_fee_per_gas=None,
        value=0,
        dry_run_only=False,
        skip_dry_run=False,
        raise_for_status=True,
        multiplier=None,
        priority=None,
        confirmation_blocks=0,
        meta: Optional[Dict] = None,
        **kwargs
    ):
        method = transaction(self, *args, **kwargs)

        nonce = get_eth_nonce(self.skale.web3, self.skale.wallet.address)

        call_result, tx_hash, receipt = None, None, None
        should_dry_run = not skip_dry_run and not config.DISABLE_DRY_RUN

        if should_dry_run:
            call_result = make_dry_run_call(self.skale, method, gas_limit, value)
            if call_result.status == TxStatus.SUCCESS:
                gas_limit = gas_limit or call_result.data['gas']

        should_send = not dry_run_only and \
            (not should_dry_run or call_result.status == TxStatus.SUCCESS)

        if should_send:
            gas_limit = gas_limit or config.DEFAULT_GAS_LIMIT
            gas_price = gas_price or config.DEFAULT_GAS_PRICE_WEI or self.skale.gas_price
            tx = transaction_from_method(
                method=method,
                gas_limit=gas_limit,
                gas_price=gas_price,
                max_fee_per_gas=max_fee_per_gas,
                max_priority_fee_per_gas=max_priority_fee_per_gas,
                nonce=nonce,
                value=value
            )
            method_name = f'{self.name}.{method.abi.get("name")}'
            tx_hash = self.skale.wallet.sign_and_send(
                tx,
                multiplier=multiplier,
                priority=priority,
                method=method_name,
                meta=meta
            )

        should_wait = tx_hash is not None and wait_for
        if should_wait:
            receipt = self.skale.wallet.wait(tx_hash)

        should_confirm = receipt is not None and confirmation_blocks > 0
        if should_confirm:
            wait_for_confirmation_blocks(self.skale.web3, confirmation_blocks)

        tx_res = TxRes(call_result, tx_hash, receipt)

        if raise_for_status:
            tx_res.raise_for_status()
        return tx_res

    return wrapper


class BaseContract:
    def __init__(self, skale, name, address, abi):
        self.skale = skale
        self.name = name
        self.address = Web3.to_checksum_address(address)
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
