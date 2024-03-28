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

from __future__ import annotations

import abc
import logging
from typing import TYPE_CHECKING

from skale_contracts import skale_contracts

from skale.wallets import BaseWallet
from skale.utils.exceptions import InvalidWalletError, EmptyWalletError
from skale.utils.web3_utils import default_gas_price, init_web3

from skale.contracts.contract_manager import ContractManager

if TYPE_CHECKING:
    from eth_typing import Address, ChecksumAddress


logger = logging.getLogger(__name__)


class EmptyPrivateKey(Exception):
    pass


class SkaleBase:
    __metaclass__ = abc.ABCMeta

    def __init__(self, endpoint, alias_or_address: str,
                 wallet=None, state_path=None,
                 ts_diff=None, provider_timeout=30):
        logger.info('Initializing skale.py, endpoint: %s, wallet: %s',
                    endpoint, type(wallet).__name__)
        self._endpoint = endpoint
        self.web3 = init_web3(endpoint,
                              state_path=state_path,
                              ts_diff=ts_diff,
                              provider_timeout=provider_timeout)
        self.network = skale_contracts.get_network_by_provider(self.web3.provider)
        self.project = self.network.get_project(self.project_name)
        self.instance = self.project.get_instance(alias_or_address)
        self.__contracts = {}
        self.__contracts_info = {}
        self.set_contracts_info()
        if wallet:
            self.wallet = wallet

    @property
    @abc.abstractmethod
    def project_name(self) -> str:
        """Name of smart contracts project"""

    @property
    def gas_price(self):
        return default_gas_price(self.web3)

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
    def set_contracts_info(self):
        return

    def init_contract_manager(self):
        self.add_lib_contract('contract_manager', ContractManager, 'ContractManager')

    def __init_contract_from_info(self, contract_info):
        if contract_info.upgradeable:
            self.init_upgradeable_contract(contract_info)
        else:
            self.add_lib_contract(
                contract_info.name,
                contract_info.contract_class,
                contract_info.contract_name
            )

    def init_upgradeable_contract(self, contract_info):
        address = self.get_contract_address(contract_info.contract_name)
        self.add_lib_contract(
            contract_info.name,
            contract_info.contract_class,
            contract_info.contract_name,
            address
        )

    def add_lib_contract(self, name: str, contract_class,
                         contract_name: str, contract_address: Address = None):
        address = contract_address or self.instance.get_contract_address(contract_name)
        logger.debug('Fetching abi for %s, address %s', name, address)
        contract_abi = self.instance.abi[contract_name]
        self.add_contract(name, contract_class(
            self, name, address, contract_abi))

    def add_contract(self, name, contract):
        self.__contracts[name] = contract

    def get_contract_address(self, name) -> ChecksumAddress:
        return self.web3.to_checksum_address(
            self.instance.get_contract_address(name)
        )

    def __get_contract_by_name(self, name):
        return self.__contracts[name]

    def __getattr__(self, name):
        if name not in self.__contracts:
            if not self.__contracts_info.get(name):
                logger.warning("%s method/contract wasn't found", name)
                return None
            logger.debug("Contract %s wasn't inited, creating now", name)
            contract_info = self.__contracts_info[name]
            self.__init_contract_from_info(contract_info)
        return self.__get_contract_by_name(name)
