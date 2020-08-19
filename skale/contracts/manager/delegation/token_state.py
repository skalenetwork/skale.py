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

from skale.contracts.base_contract import BaseContract


class TokenState(BaseContract):
    """Wrapper for TokenState.sol functions"""

    def get_and_update_locked_amount(self, holder_address: str) -> int:
        """This method is for check quantity of `freezed` tokens
           :param holder_address: Address of the holder
           :type holder_address: str
           :returns:
           :rtype: int
        """

        return self.contract.functions.getAndUpdateLockedAmount(holder_address).call()
