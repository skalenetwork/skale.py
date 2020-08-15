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

import abc
import logging

from web3 import Web3
from web3.middleware import geth_poa_middleware

from skale.wallets import BaseWallet
from skale.utils.web3_utils import get_provider
from skale.utils.abi_utils import get_contract_address_by_name, get_contract_abi_by_name
from skale.utils.exceptions import InvalidWalletError, EmptyWalletError

logger = logging.getLogger(__name__)


class EmptyPrivateKey(Exception):
    pass


class SkaleBase:
    __metaclass__ = abc.ABCMeta

    def __init__(self, endpoint, abi_filepath, wallet=None, provider_timeout=30, ):
        logger.info(f'Init skale-py, connecting to {endpoint}')
        provider = get_provider(endpoint, timeout=provider_timeout)
        self._abi_filepath = abi_filepath
        self._endpoint = endpoint
        self.web3 = Web3(provider)
        self.web3.middleware_onion.inject(
            geth_poa_middleware, layer=0)  # todo: may cause issues
        self.__contracts = {}
        if wallet:
            self.wallet = wallet
        self.init_contracts()

    @property
    def gas_price(self):
        return self.web3.eth.gasPrice * 5 // 4

    @property
    def wallet(self):
        if not self._wallet:
            raise EmptyWalletError('No wallet provided')
        return self._wallet

    @wallet.setter
    def wallet(self, wallet):
        if issubclass(type(wallet), BaseWallet):
            self._wallet = wallet
        else:
            raise InvalidWalletError(f'Wrong wallet class: {type(wallet).__name__}. \
                                       Must be one of the BaseWallet subclasses')

    def __is_debug_contracts(self, abi):
        return abi.get('time_helpers_with_debug_address', None)

    @abc.abstractmethod
    def init_contracts(self):
        return

    def __init_contracts_from_info(self, abi, contracts_info):
        for name in contracts_info:
            info = contracts_info[name]
            if info.upgradeable:
                self.init_upgradeable_contract(info, abi)
            else:
                self.add_lib_contract(info.name, info.contract_class, abi)

    def init_upgradeable_contract(self, contract_info, abi):
        address = self.get_contract_address(contract_info.contract_name)
        self.add_lib_contract(contract_info.name, contract_info.contract_class,
                              abi, address)

    def add_lib_contract(self, name, contract_class, abi, contract_address=None):
        address = contract_address or get_contract_address_by_name(
            abi, name)
        logger.info(f'Fetching abi for {name}, address {address}')
        contract_abi = get_contract_abi_by_name(abi, name)
        self.add_contract(name, contract_class(
            self, name, address, contract_abi))

    def add_contract(self, name, skale_contract):
        logger.debug(f'Init contract: {name}')
        self.__contracts[name] = skale_contract

    def get_contract_address(self, name):
        return self.contract_manager.get_contract_address(name)

    def get_contract_by_name(self, name):
        return self.__contracts[name]

    def __getattr__(self, name):
        if name not in self.__contracts:
            return None
        return self.get_contract_by_name(name)
