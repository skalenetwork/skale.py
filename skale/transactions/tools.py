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


import logging
import time
from functools import partial, wraps
from typing import Any, Callable, Optional, TYPE_CHECKING

from eth_typing import ChecksumAddress
from web3 import Web3
from web3.contract.contract import ContractFunction
from web3.exceptions import ContractLogicError, Web3Exception
from web3._utils.transactions import get_block_gas_limit
from web3.types import Nonce, TxParams, Wei

import skale.config as config
from skale.transactions.exceptions import TransactionError
from skale.transactions.result import TxCallResult, TxRes, TxStatus
from skale.utils.web3_utils import get_eth_nonce

if TYPE_CHECKING:
    from skale.skale_base import SkaleBase


logger = logging.getLogger(__name__)


DEFAULT_ETH_SEND_GAS_LIMIT = 22000


def make_dry_run_call(
    skale: 'SkaleBase', method: ContractFunction, gas_limit: int | None = None, value: Wei = Wei(0)
) -> TxCallResult:
    opts = TxParams({'from': skale.wallet.address, 'value': value})
    logger.info(
        f'Dry run tx: {method.fn_name}, '
        f'sender: {skale.wallet.address}, '
        f'wallet: {skale.wallet.__class__.__name__}, '
        f'value: {value}, '
    )
    estimated_gas = 0

    try:
        if gas_limit:
            estimated_gas = gas_limit
            opts.update({'gas': gas_limit})
            method.call(opts)
        else:
            estimated_gas = estimate_gas(skale.web3, method, opts)
        logger.info(f'Estimated gas for {method.fn_name}: {estimated_gas}')
    except ContractLogicError as e:
        message = e.message or 'Contract logic error'
        error_data = e.data or {}
        data = {'data': error_data} if isinstance(error_data, str) else error_data
        return TxCallResult(status=TxStatus.FAILED, error='revert', message=message, data=data)
    except (Web3Exception, ValueError) as e:
        logger.exception('Dry run for %s failed', method)
        return TxCallResult(status=TxStatus.FAILED, error='exception', message=str(e), data={})

    return TxCallResult(
        status=TxStatus.SUCCESS, error='', message='success', data={'gas': estimated_gas}
    )


def estimate_gas(web3: Web3, method: ContractFunction, opts: TxParams) -> int:
    try:
        block_gas_limit = get_block_gas_limit(web3)
    except AttributeError:
        block_gas_limit = get_block_gas_limit(web3)

    estimated_gas = method.estimate_gas(opts, block_identifier='latest')
    normalized_estimated_gas = int(estimated_gas * config.DEFAULT_GAS_MULTIPLIER)
    if normalized_estimated_gas > block_gas_limit:
        logger.warning(
            f'Estimate gas for {method.fn_name} - {normalized_estimated_gas} exceeds \
block gas limit, going to use block_gas_limit ({block_gas_limit}) for this transaction'
        )
        return block_gas_limit
    return normalized_estimated_gas


def build_tx_dict(method: ContractFunction, *args: Any, **kwargs: Any) -> TxParams:
    base_fields = compose_base_fields(*args, **kwargs)
    return method.build_transaction(base_fields)


def compose_base_fields(
    nonce: Nonce,
    gas_limit: int,
    gas_price: Wei | None = None,
    max_fee_per_gas: Wei | None = None,
    max_priority_fee_per_gas: Wei | None = None,
    value: Wei = Wei(0),
) -> TxParams:
    fee_fields = TxParams({'gas': gas_limit, 'nonce': nonce, 'value': value})
    if max_priority_fee_per_gas is not None and max_fee_per_gas is not None:
        fee_fields.update(
            {'maxPriorityFeePerGas': max_priority_fee_per_gas, 'maxFeePerGas': max_fee_per_gas}
        )
        fee_fields.update({'type': 2})
    elif gas_price is not None:
        fee_fields.update({'gasPrice': gas_price})
        fee_fields.update({'type': 1})
    return fee_fields


def transaction_from_method(
    method: ContractFunction,
    *,
    multiplier: Optional[float] = None,
    priority: Optional[int] = None,
    **kwargs: Any,
) -> TxParams:
    tx = build_tx_dict(method, **kwargs)
    logger.info(f'Tx: {method.fn_name}, Fields: {tx}, ')
    return tx


def compose_eth_transfer_tx(
    web3: Web3,
    from_address: ChecksumAddress,
    to_address: ChecksumAddress,
    value: Wei,
    **kwargs: Any,
) -> TxParams:
    nonce = get_eth_nonce(web3, from_address)
    base_fields = compose_base_fields(
        nonce=nonce, gas_limit=DEFAULT_ETH_SEND_GAS_LIMIT, value=value, **kwargs
    )
    tx = TxParams({'from': from_address, 'to': to_address, **base_fields})
    return tx


def retry_tx(
    tx: Callable[..., TxRes] | None = None, *, max_retries: int = 3, timeout: int = -1
) -> Callable[..., TxRes | None] | partial[Any]:
    if tx is None:
        return partial(retry_tx, max_retries=3, timeout=timeout)

    @wraps(tx)
    def wrapper(*args: Any, **kwargs: Any) -> TxRes | None:
        return run_tx_with_retry(
            tx, *args, max_retries=max_retries, retry_timeout=timeout, **kwargs
        )

    return wrapper


def run_tx_with_retry(
    transaction: Callable[..., TxRes],
    *args: Any,
    max_retries: int = 3,
    retry_timeout: int = -1,
    raise_for_status: bool = True,
    **kwargs: Any,
) -> TxRes | None:
    attempt = 0
    tx_res = None
    exp_timeout = 1
    error = None
    while attempt < max_retries:
        try:
            tx_res = transaction(*args, raise_for_status=raise_for_status, **kwargs)
            tx_res.raise_for_status()
        except TransactionError as e:
            error = e
            logger.exception('Tx attempt %d/%d failed', attempt + 1, max_retries)

            timeout = exp_timeout if retry_timeout < 0 else exp_timeout
            time.sleep(timeout)
            exp_timeout *= 2
        else:
            error = None
            break
        attempt += 1
    if error is None:
        logger.info(
            'Tx %s completed after %d/%d retries', transaction.__name__, attempt + 1, max_retries
        )
    else:
        logger.error('Tx %s failed after %d retries', transaction.__name__, max_retries)
        if raise_for_status:
            raise error
    if tx_res is not None:
        tx_res.attempts = attempt
    return tx_res
