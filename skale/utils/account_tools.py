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
"""Account utilities"""

from __future__ import annotations
from decimal import Decimal
import logging
from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, Type, TypedDict

from eth_typing import ChecksumAddress, HexStr
from web3 import Web3
from web3.types import TxReceipt, Wei

from skale.transactions.result import TxRes
from skale.transactions.tools import compose_eth_transfer_tx
from skale.utils.constants import LONG_LINE
from skale.wallets import LedgerWallet, Web3Wallet
from skale.utils.web3_utils import check_receipt, default_gas_price, wait_for_confirmation_blocks

if TYPE_CHECKING:
    from skale.skale_manager import SkaleManager
    from skale.wallets.common import BaseWallet


logger = logging.getLogger(__name__)


class AccountData(TypedDict):
    address: ChecksumAddress
    private_key: HexStr


WALLET_TYPE_TO_CLASS: Dict[str, Type[LedgerWallet] | Type[Web3Wallet]] = {
    'ledger': LedgerWallet,
    'web3': Web3Wallet,
}


def create_wallet(
    wallet_type: Literal['web3'] | Literal['ledger'] = 'web3', *args: Any, **kwargs: Any
) -> LedgerWallet | Web3Wallet:
    return WALLET_TYPE_TO_CLASS[wallet_type](*args, **kwargs)


def send_tokens(
    skale: SkaleManager, receiver_address: ChecksumAddress, amount: Wei, *args: Any, **kwargs: Any
) -> TxRes:
    logger.info(f'Sending {amount} SKALE tokens from {skale.wallet.address} => {receiver_address}')

    wei_amount = skale.web3.to_wei(amount, 'ether')
    return skale.token.transfer(receiver_address, wei_amount, *args, **kwargs)


def send_eth(
    web3: Web3,
    wallet: BaseWallet,
    receiver_address: ChecksumAddress,
    amount: Wei,
    *args: Any,
    gas_price: Optional[int] = None,
    wait_for: bool = True,
    confirmation_blocks: int = 0,
    multiplier: Optional[int] = None,
    priority: Optional[int] = None,
    **kwargs: Any,
) -> TxReceipt:
    logger.info(f'Sending {amount} ETH from {wallet.address} => {receiver_address}')
    wei_amount = web3.to_wei(amount, 'ether')
    gas_price = gas_price or default_gas_price(web3)
    tx = compose_eth_transfer_tx(
        web3, wallet.address, receiver_address, wei_amount, gas_price=gas_price, *args, **kwargs
    )
    tx_hash = wallet.sign_and_send(tx, multiplier=multiplier, priority=priority)
    if wait_for:
        receipt = wallet.wait(tx_hash)
    if confirmation_blocks:
        wait_for_confirmation_blocks(web3, confirmation_blocks)
    check_receipt(receipt)
    return receipt


def account_eth_balance_wei(web3: Web3, address: ChecksumAddress) -> Wei:
    return web3.eth.get_balance(address)


def check_ether_balance(web3: Web3, address: ChecksumAddress) -> int | Decimal:
    balance_wei = account_eth_balance_wei(web3, address)
    balance = web3.from_wei(balance_wei, 'ether')

    logger.info(f'{address} balance: {balance} ETH')
    return balance


def check_skale_balance(skale: SkaleManager, address: ChecksumAddress) -> int | Decimal:
    balance_wei = skale.token.get_balance(address)
    balance = skale.web3.from_wei(balance_wei, 'ether')
    logger.info(f'{address} balance: {balance} SKALE')
    return balance


def generate_account(web3: Web3) -> AccountData:
    account = web3.eth.account.create()
    private_key = account.key.hex()
    logger.info(f'Generated account: {account.address}')
    return AccountData({'address': account.address, 'private_key': private_key})


def generate_accounts(
    skale: SkaleManager,
    base_wallet: BaseWallet,
    n_wallets: int,
    skale_amount: Wei,
    eth_amount: Wei,
    debug: bool = False,
) -> List[AccountData]:
    n_wallets = int(n_wallets)
    results = []

    for _ in range(0, n_wallets):
        wallet = generate_account(skale.web3)

        send_tokens(skale, wallet['address'], skale_amount)
        send_eth(skale.web3, skale.wallet, wallet['address'], eth_amount)

        if debug:
            check_ether_balance(skale.web3, wallet['address'])
            check_skale_balance(skale, wallet['address'])

        results.append(wallet)
        logger.info(LONG_LINE)

    return results
