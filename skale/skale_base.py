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

from skale_contracts import skale_contracts
from skale_contracts.project_factory import SkaleProject

from skale.utils.exceptions import InvalidWalletError, EmptyWalletError
from skale.utils.web3_utils import default_gas_price, init_web3, get_endpoint
from skale.wallets import BaseWallet


logger = logging.getLogger(__name__)


class EmptyPrivateKey(Exception):
    pass


class SkaleBase:
    __metaclass__ = abc.ABCMeta

    def __init__(
        self,
        endpoint: str | list[str],
        alias_or_address: str,
        wallet: BaseWallet | None = None,
        state_path: str | None = None,
        ts_diff: int | None = None,
        provider_timeout: int = 30,
        debug: bool = False,
    ):
        logger.info(
            'Initializing %s, endpoint: %s, alias_or_address: %s, wallet: %s',
            self.__class__.__name__,
            endpoint,
            alias_or_address,
            type(wallet).__name__,
        )
        if state_path:
            logger.warning(
                'state_path is deprecated and will be ignored. This option will be removed in v8.'
            )
        self._endpoint = get_endpoint(endpoint)
        self._alias_or_address = alias_or_address
        self.web3 = init_web3(self._endpoint, ts_diff=ts_diff, provider_timeout=provider_timeout)
        self.network = skale_contracts.get_network_by_provider(self.web3.provider)
        self.project = self.network.get_project(self.project_name)
        self.instance = self.project.get_instance(alias_or_address)
        self.debug = debug
        if wallet:
            self.wallet = wallet

    @property
    @abc.abstractmethod
    def project_name(self) -> SkaleProject:
        """Name of smart contracts project"""

    @property
    def gas_price(self) -> int:
        return default_gas_price(self.web3)

    @property
    def wallet(self) -> BaseWallet:
        if not self._wallet:
            raise EmptyWalletError('No wallet provided')
        return self._wallet

    @wallet.setter
    def wallet(self, wallet: BaseWallet) -> None:
        if issubclass(type(wallet), BaseWallet):
            self._wallet = wallet
        else:
            raise InvalidWalletError(
                f'Wrong wallet class: {type(wallet).__name__}. \
                Must be one of the BaseWallet subclasses'
            )
