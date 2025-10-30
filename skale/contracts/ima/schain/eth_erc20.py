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

from time import sleep

from eth_typing import ChecksumAddress
from web3.types import Wei

from skale.contracts.skale_contract import SkaleContract


class EthErc20(SkaleContract):
    def balance_of(self, address: ChecksumAddress) -> Wei:
        return Wei(self.contract.functions.balanceOf(address).call())

    def wait_for_balance_change(
        self,
        address: ChecksumAddress,
        initial_balance: Wei,
        timeout: int = 120,
        poll_interval: int = 5,
        raise_on_timeout: bool = False,
    ) -> bool:
        iterations = timeout // poll_interval + 1
        for _ in range(iterations):
            current_balance = self.balance_of(address)
            if current_balance != initial_balance:
                return True
            sleep(poll_interval)

        if raise_on_timeout:
            raise TimeoutError(f'Balance did not change for {address} within {timeout} seconds')
        return False
