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

from skale.transactions.result import (
    DryRunFailedError,
    InsufficientBalanceError,
    TransactionFailedError, TxRes
)
from skale.utils.constants import GAS_LIMIT_COEFFICIENT
from skale.utils.exceptions import RPCWalletError
from skale.utils.web3_utils import get_eth_nonce

from web3._utils.transactions import get_block_gas_limit

logger = logging.getLogger(__name__)


def make_dry_run_call(skale, method, gas_limit=None) -> dict:
    opts = {
        'from': skale.wallet.address,
    }
    logger.info(
        f'Dry run tx: {method.fn_name}, '
        f'sender: {skale.wallet.address}, '
        f'wallet: {skale.wallet.__class__.__name__}, '
    )
    try:
        if gas_limit:
            estimated_gas = gas_limit
            opts.update({'gas': gas_limit})
            method.call(opts)
        else:
            estimated_gas = estimate_gas(skale.web3, method, opts)
        logger.info(f'Estimated gas for {method.fn_name}: {estimated_gas}')
    except Exception as err:
        logger.error('Dry run for method failed with error', exc_info=err)
        return {'status': 0, 'error': str(err)}

    return {'status': 1, 'payload': estimated_gas}


def estimate_gas(web3, method, opts):
    try:
        block_gas_limit = get_block_gas_limit(web3)
    except AttributeError:
        block_gas_limit = get_block_gas_limit(web3)
    estimated_gas = method.estimateGas(opts)
    normalized_estimated_gas = int(estimated_gas * GAS_LIMIT_COEFFICIENT)
    if normalized_estimated_gas > block_gas_limit:
        logger.warning(f'Estimate gas for {method.fn_name} exceeds block gas limit')
        return block_gas_limit
    return normalized_estimated_gas


def build_tx_dict(method, gas_limit, gas_price=None, nonce=None):
    tx_dict_fields = {
        'gas': gas_limit,
        'nonce': nonce
    }
    if gas_price is not None:
        tx_dict_fields.update({'gasPrice': gas_price})

    return method.buildTransaction(tx_dict_fields)


def sign_and_send(web3, method, gas_amount, wallet) -> hash:
    nonce = get_eth_nonce(web3, wallet.address)
    tx_dict = build_tx_dict(method, gas_amount, nonce)
    signed_tx = wallet.sign(tx_dict)
    return web3.eth.sendRawTransaction(signed_tx.rawTransaction)


def post_transaction(wallet, method, gas_limit, gas_price=None, nonce=None) -> str:
    logger.info(
        f'Tx: {method.fn_name}, '
        f'sender: {wallet.address}, '
        f'wallet: {wallet.__class__.__name__}, '
        f'gasLimit: {gas_limit}, '
        f'gasPrice: {gas_price}'
    )
    tx_dict = build_tx_dict(method, gas_limit, gas_price, nonce)
    tx_hash = wallet.sign_and_send(tx_dict)
    return tx_hash


def send_eth(web3, account, amount, wallet):
    eth_nonce = get_eth_nonce(web3, wallet.address)
    logger.info(f'Transaction nonce {eth_nonce}')
    txn = {
        'to': account,
        'value': amount,
        'gasPrice': web3.eth.gasPrice,
        'gas': 22000,
        'nonce': eth_nonce
    }
    signed_txn = wallet.sign(txn)
    tx = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

    logger.info(
        f'ETH transfer {wallet.address} => {account}, {amount} wei,'
        f'tx: {web3.toHex(tx)}'
    )
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
                      **kwargs) -> TxRes:
    success = False
    attempt = 0
    tx_res = None
    exp_timeout = 1
    while not success and attempt < max_retries:
        try:
            tx_res = transaction(*args, **kwargs)
            tx_res.raise_for_status()
        except (TransactionFailedError, DryRunFailedError, RPCWalletError) as err:
            logger.error(f'Tx attempt {attempt}/{max_retries} failed',
                         exc_info=err)
            timeout = exp_timeout if retry_timeout < 0 else exp_timeout
            time.sleep(timeout)
            exp_timeout *= 2
        except InsufficientBalanceError as err:
            logger.error('Sender balance is too low', exc_info=err)
            raise err
        else:
            success = True
        attempt += 1
    if success:
        logger.info(f'Tx {transaction.__name__} completed '
                    f'after {attempt}/{max_retries} retries')
    else:
        logger.error(
            f'Tx {transaction.__name__} failed after '
            f'{max_retries} retries')
    return tx_res
