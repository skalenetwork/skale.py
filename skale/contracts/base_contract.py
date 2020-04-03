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

from skale.transactions.tools import post_transaction, make_call
from skale.utils.web3_utils import (TransactionFailedError,
                                    wait_for_receipt_by_blocks)


logger = logging.getLogger(__name__)


def transaction_method(gas_limit):
    def real_decorator(transaction):
        @wraps(transaction)
        def wrapper(self, *args, wait_for=False, timeout=4, blocks_to_wait=50, retries=1,
                    gas_price=None, nonce=None, dry_run=False, **kwargs):
            method = transaction(self, *args, **kwargs)
            if dry_run:
                opts = {
                    'from': self.skale.wallet.address,
                    'gas': gas_limit
                }
                logger.info(
                    f'transaction_method: {transaction.__name__} - dry_run, '
                    f'sender: {self.skale.wallet.address}, '
                    f'gas: {gas_limit}'
                )
                return make_call(method, opts)
            else:
                for retry in range(retries):
                    logger.info(
                        f'transaction_method: {transaction.__name__}, try {retry+1}/{retries}, '
                        f'wallet: {self.skale.wallet.__class__.__name__}, '
                        f'sender: {self.skale.wallet.address}, '
                        f'gas: {gas_limit}'
                    )
                    tx_res = post_transaction(self.skale.wallet, method, gas_limit, gas_price,
                                              nonce)
                    if wait_for:
                        tx_res.receipt = wait_for_receipt_by_blocks(
                            self.skale.web3,
                            tx_res.hash,
                            timeout=timeout,
                            blocks_to_wait=blocks_to_wait
                        )
                        if tx_res.receipt['status'] == 1:
                            return tx_res
                    else:
                        return tx_res
                raise TransactionFailedError(
                    f'transaction_method failed: {transaction.__name__}, '
                    f'receipt: {tx_res.receipt}'
                )
        return wrapper
    return real_decorator


class BaseContract:
    def __init__(self, skale, name, address, abi):
        self.skale = skale
        self.name = name
        self.address = Web3.toChecksumAddress(address)
        self.contract = skale.web3.eth.contract(address=self.address, abi=abi)
