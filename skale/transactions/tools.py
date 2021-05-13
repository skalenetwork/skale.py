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

import skale.config as config
from skale.transactions.result import (
    DryRunFailedError,
    InsufficientBalanceError,
    TransactionFailedError, TxRes
)
from skale.utils.constants import GAS_LIMIT_COEFFICIENT
from skale.utils.exceptions import RPCWalletError
from skale.utils.web3_utils import (
    check_receipt,
    get_eth_nonce,
    wait_for_receipt_by_blocks,
)

from web3._utils.transactions import get_block_gas_limit

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
        logger.warning(f'Estimate gas for {method.fn_name} - {normalized_estimated_gas} exceeds \
block gas limit, going to use block_gas_limit ({block_gas_limit}) for this transaction')
        return block_gas_limit
    return normalized_estimated_gas


def build_tx_dict(method, gas_limit, gas_price=None, nonce=None, value=0):
    tx_dict_fields = {
        'gas': gas_limit,
        'nonce': nonce,
        'value': value
    }
    if gas_price is not None:
        tx_dict_fields.update({'gasPrice': gas_price})

    return method.buildTransaction(tx_dict_fields)


def sign_and_send(web3, method, gas_amount, wallet) -> hash:
    nonce = get_eth_nonce(web3, wallet.address)
    tx_dict = build_tx_dict(method, gas_amount, nonce)
    signed_tx = wallet.sign(tx_dict)
    return web3.eth.sendRawTransaction(signed_tx.rawTransaction)


def post_transaction(wallet, method, gas_limit, gas_price=None, nonce=None, value=0) -> str:
    logger.info(
        f'Tx: {method.fn_name}, '
        f'sender: {wallet.address}, '
        f'wallet: {wallet.__class__.__name__}, '
        f'gasLimit: {gas_limit}, '
        f'gasPrice: {gas_price}, '
        f'value: {value}'
    )
    tx_dict = build_tx_dict(method, gas_limit, gas_price, nonce, value)
    tx_hash = wallet.sign_and_send(tx_dict)
    return tx_hash


def send_eth_with_skale(skale, address: str, amount_wei: int, *,
                        gas_limit: int = DEFAULT_ETH_SEND_GAS_LIMIT,
                        gas_price: int = None,
                        nonce: int = None, wait_for=True):
    gas_limit = gas_limit or DEFAULT_ETH_SEND_GAS_LIMIT
    gas_price = gas_price or skale.web3.eth.gasPrice
    tx = {
        'to': address,
        'value': amount_wei,
        'gasPrice': gas_price,
        'gas': gas_limit,
        'nonce': nonce
    }
    logger.info(f'Sending {amount_wei} WEI to {address}')
    tx_hash = skale.wallet.sign_and_send(tx)
    logger.info(f'Waiting for receipt for {tx_hash}')

    if wait_for:
        receipt = wait_for_receipt_by_blocks(skale.web3, tx_hash)
        check_receipt(receipt)
        return receipt
    return tx_hash


def send_eth(web3, account, amount, wallet, gas_price=None):
    eth_nonce = get_eth_nonce(web3, wallet.address)
    logger.info(f'Transaction nonce {eth_nonce}')
    gas_price = gas_price or config.DEFAULT_GAS_PRICE_WEI or web3.eth.gasPrice
    txn = {
        'to': account,
        'value': amount,
        'gasPrice': gas_price,
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
