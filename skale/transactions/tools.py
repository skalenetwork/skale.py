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
from typing import Dict, Optional

from web3 import Web3
from web3.exceptions import ContractLogicError, Web3Exception
from web3._utils.transactions import get_block_gas_limit

import skale.config as config
from skale.transactions.exceptions import TransactionError
from skale.transactions.result import TxRes
from skale.utils.web3_utils import get_eth_nonce


logger = logging.getLogger(__name__)


DEFAULT_ETH_SEND_GAS_LIMIT = 22000


def make_dry_run_call(skale, method, gas_limit=None, value=0) -> dict:
    opts = {
        'from': skale.wallet.address,
        'value': value
    }
    logger.info(
        f'Dry run tx: {method.fn_name}, '
        f'sender: {skale.wallet.address}, '
        f'wallet: {skale.wallet.__class__.__name__}, '
        f'value: {value}, '
    )

    try:
        if gas_limit:
            estimated_gas = gas_limit
            opts.update({'gas': gas_limit})
            method.call(opts)
        else:
            estimated_gas = estimate_gas(skale.web3, method, opts)
        logger.info(f'Estimated gas for {method.fn_name}: {estimated_gas}')
    except ContractLogicError as e:
        return {'status': 0, 'error': 'revert', 'message': e.message, 'data': e.data}
    except (Web3Exception, ValueError) as err:
        logger.error('Dry run for %s failed', method, exc_info=err)
        return {'status': 0, 'error': str(err)}

    return {'status': 1, 'payload': estimated_gas}


def estimate_gas(web3, method, opts):
    try:
        block_gas_limit = get_block_gas_limit(web3)
    except AttributeError:
        block_gas_limit = get_block_gas_limit(web3)

    estimated_gas = method.estimate_gas(
        opts,
        block_identifier='latest'
    )
    normalized_estimated_gas = int(
        estimated_gas * config.DEFAULT_GAS_MULTIPLIER
    )
    if normalized_estimated_gas > block_gas_limit:
        logger.warning(f'Estimate gas for {method.fn_name} - {normalized_estimated_gas} exceeds \
block gas limit, going to use block_gas_limit ({block_gas_limit}) for this transaction')
        return block_gas_limit
    return normalized_estimated_gas


def build_tx_dict(method, *args, **kwargs):
    base_fields = compose_base_fields(*args, **kwargs)
    return method.build_transaction(base_fields)


def compose_base_fields(
    nonce: int,
    gas_limit: int,
    gas_price: Optional[int] = None,
    max_fee_per_gas: Optional[int] = None,
    max_priority_fee_per_gas: Optional[int] = None,
    value: Optional[int] = 0,
) -> Dict:
    fee_fields = {
        'gas': gas_limit,
        'nonce': nonce,
        'value': value
    }
    if max_priority_fee_per_gas is not None:
        fee_fields.update({
            'maxPriorityFeePerGas': max_priority_fee_per_gas,
            'maxFeePerGas': max_fee_per_gas
        })
        fee_fields.update({'type': 2})
    elif gas_price is not None:
        fee_fields.update({'gasPrice': gas_price})
        fee_fields.update({'type': 1})
    return fee_fields


def transaction_from_method(
    method,
    *,
    multiplier: Optional[float] = None,
    priority: Optional[int] = None,
    **kwargs
) -> str:
    tx = build_tx_dict(method, **kwargs)
    logger.info(
        f'Tx: {method.fn_name}, '
        f'Fields: {tx}, '
    )
    return tx


def compose_eth_transfer_tx(
    web3: Web3,
    from_address: str,
    to_address: str,
    value: int,
    **kwargs
) -> Dict:
    nonce = get_eth_nonce(web3, from_address)
    base_fields = compose_base_fields(
        nonce=nonce,
        gas_limit=DEFAULT_ETH_SEND_GAS_LIMIT,
        value=value,
        **kwargs
    )
    tx = {
        'from': from_address,
        'to': to_address,
        **base_fields
    }
    return tx


def retry_tx(tx=None, *, max_retries=3, timeout=-1):
    if tx is None:
        return partial(retry_tx, max_retries=3, timeout=timeout)

    @wraps(tx)
    def wrapper(*args, **kwargs):
        return run_tx_with_retry(
            tx, *args,
            max_retries=max_retries,
            retry_timeout=timeout, **kwargs
        )
    return wrapper


def run_tx_with_retry(transaction, *args, max_retries=3,
                      retry_timeout=-1,
                      raise_for_status=True,
                      **kwargs) -> TxRes:
    attempt = 0
    tx_res = None
    exp_timeout = 1
    error = None
    while attempt < max_retries:
        try:
            tx_res = transaction(
                *args,
                raise_for_status=raise_for_status,
                **kwargs
            )
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
            'Tx %s completed after %d/%d retries',
            transaction.__name__, attempt + 1, max_retries
        )
    else:
        logger.error(
            'Tx %s completed after %d retries',
            transaction.__name__, max_retries
        )
        if raise_for_status:
            raise error
    return tx_res
