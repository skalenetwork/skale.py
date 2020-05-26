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

from web3 import Web3
from web3.middleware import geth_poa_middleware

import skale.contracts as contracts
from skale.wallets import BaseWallet
from skale.contracts_info import get_base_contracts_info, get_debug_contracts_info
from skale.utils.helper import get_abi
from skale.utils.web3_utils import get_provider
from skale.utils.exceptions import InvalidWalletError, EmptyWalletError

logger = logging.getLogger(__name__)


class EmptyPrivateKey(Exception):
    pass


def spawn_skale_lib(skale):
    return Skale(skale._endpoint, skale._abi_filepath, skale.wallet)


class Skale:
    def __init__(self, endpoint, abi_filepath, wallet=None, provider_timeout=30):
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
        self.__init_contracts(get_abi(abi_filepath))

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

    def __init_contracts(self, abi):
        self.add_lib_contract('contract_manager',
                              contracts.ContractManager, abi)
        self.__init_contracts_from_info(abi, get_base_contracts_info())
        if self.__is_debug_contracts(abi):
            logger.info('Debug contracts found in ABI file')
            self.__init_contracts_from_info(abi, get_debug_contracts_info())

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
        address = contract_address or self.get_contract_address_by_name(
            abi, name)
        logger.info(f'Fetching abi for {name}, address {address}')
        if name == 'dkg':  # todo: tmp fix
            contract_abi = self.get_contract_abi_by_name(abi, 'd_k_g')
        elif name == 'nodes_data':
            contract_abi = self.get_contract_abi_by_name(abi, 'nodes')
        else:
            contract_abi = self.get_contract_abi_by_name(abi, name)
        self.add_contract(name, contract_class(
            self, name, address, contract_abi))

    def get_contract_address_by_name(self, abi, name):
        if name == 'dkg':  # todo: tmp fix
            return abi.get(f'skale_d_k_g_address')
        if name == 'nodes_data':
            return abi.get(f'nodes_address')
        return abi.get(f'skale_{name}_address') or abi.get(f'{name}_address')

    def get_contract_abi_by_name(self, abi, name):  # todo: unify abi key names
        return abi.get(f'skale_{name}_abi') or abi.get(
            f'{name}_abi') or abi.get(f'{name}_functionality_abi') or abi.get(
            f'{name}_data_abi')

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
