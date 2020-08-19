#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2020-Present SKALE Labs
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

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes
from skale.utils.constants import GAS


class TimeHelpersWithDebug(BaseContract):
    """Wrapper for TimeHelpersWithDebug.sol functions (internal usage only)"""

    @transaction_method(gas_limit=GAS['skip_time'])
    def skip_time(self, sec: int) -> TxRes:
        """Skip time on contracts

        :param sec: Time to skip in seconds
        :type sec: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.skipTime(sec)

    def get_current_month(self) -> int:
        """Get current month from contract

        :returns: Month index
        :rtype: int
        """
        return self.contract.functions.getCurrentMonth().call()
