#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2025-Present SKALE Labs
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

import logging
from functools import wraps
from typing import Any, Callable, cast

from eth_typing import ChecksumAddress
from web3 import Web3
from web3.contract.contract import ContractFunction
from web3.types import Nonce, Wei

import skale.config as config
from skale.transactions.result import TxRes, TxStatus
from skale.transactions.tools import make_dry_run_call, transaction_from_method
from skale.utils.helper import to_camel_case
from skale.utils.web3_utils import (
    DEFAULT_BLOCKS_TO_WAIT,
    MAX_WAITING_TIME,
    default_gas_price,
    get_eth_nonce,
    wait_for_confirmation_blocks,
)
from skale.wallets.common import BaseWallet

logger = logging.getLogger(__name__)


class BaseContract:
    def __init__(
        self,
        web3: Web3,
        address: ChecksumAddress,
        abi: list[Any],
        wallet: BaseWallet | None = None,
    ):
        self.web3 = web3
        self._wallet = wallet
        self._init_contract(address, abi)

    @property
    def wallet(self) -> BaseWallet | None:
        return self._wallet

    @wallet.setter
    def wallet(self, value: BaseWallet | None) -> None:
        self._wallet = value

    def _init_contract(self, address: ChecksumAddress, abi: list[Any]) -> None:
        self.address = Web3.to_checksum_address(address)
        self.contract = self.web3.eth.contract(address=self.address, abi=abi)

    def __getattr__(self, attr: str) -> Callable[..., Any]:
        """Fallback for contract calls"""
        logger.debug('Calling contract function: %s', attr)

        def wrapper(*args: Any, **kw: Any) -> Any:
            logger.debug('called with %r and %r' % (args, kw))
            camel_case_fn_name = to_camel_case(attr)
            if hasattr(self.contract.functions, camel_case_fn_name):
                return getattr(self.contract.functions, camel_case_fn_name)(*args, **kw).call()
            if hasattr(self.contract.functions, attr):
                return getattr(self.contract.functions, attr)(*args, **kw).call()
            raise AttributeError(attr)

        return wrapper


def transaction_method(transaction: Callable[..., ContractFunction]) -> Callable[..., TxRes]:
    @wraps(transaction)
    def wrapper(
        self: BaseContract,
        *args: Any,
        wait_for: bool = True,
        blocks_to_wait: int = DEFAULT_BLOCKS_TO_WAIT,
        timeout: int = MAX_WAITING_TIME,
        gas_limit: int | None = None,
        gas_price: int | None = None,
        nonce: Nonce | None = None,
        max_fee_per_gas: int | None = None,
        max_priority_fee_per_gas: int | None = None,
        value: Wei = Wei(0),
        dry_run_only: bool = False,
        skip_dry_run: bool = False,
        raise_for_status: bool = True,
        multiplier: float | None = None,
        priority: int | None = None,
        confirmation_blocks: int = 0,
        **kwargs: Any,
    ) -> TxRes:
        if not self.wallet:
            raise ValueError('Wallet is not set for this contract')
        method = transaction(self, *args, **kwargs)

        nonce = get_eth_nonce(self.web3, self.wallet.address)

        call_result, tx_hash, receipt = None, None, None
        should_dry_run = not skip_dry_run and not config.DISABLE_DRY_RUN

        dry_run_success = False
        if should_dry_run:
            call_result = make_dry_run_call(self.web3, self.wallet, method, gas_limit, value)
            if call_result.status == TxStatus.SUCCESS:
                gas_limit = gas_limit or int(call_result.data['gas'])
                dry_run_success = True

        should_send = not dry_run_only and (not should_dry_run or dry_run_success)
        if should_send:
            gas_limit = gas_limit or config.DEFAULT_GAS_LIMIT
            gas_price = gas_price or config.DEFAULT_GAS_PRICE_WEI or default_gas_price(self.web3)
            tx = transaction_from_method(
                method=method,
                gas_limit=gas_limit,
                gas_price=gas_price,
                max_fee_per_gas=max_fee_per_gas,
                max_priority_fee_per_gas=max_priority_fee_per_gas,
                nonce=nonce,
                value=value,
            )
            method_name = f'{self.name}.{method.abi.get("name")}'
            tx_hash = self.wallet.sign_and_send(
                tx, multiplier=multiplier, priority=priority, method=method_name
            )

        if tx_hash is not None and wait_for:
            receipt = self.wallet.wait(tx_hash)

        should_confirm = receipt is not None and confirmation_blocks > 0
        if should_confirm:
            wait_for_confirmation_blocks(self.web3, confirmation_blocks)

        tx_res = TxRes(call_result, tx_hash, receipt)

        if raise_for_status:
            tx_res.raise_for_status()
        return tx_res

    # return wrapper
    return cast(Callable[..., TxRes], wrapper)
