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

from skale.contracts import BaseContract
from skale.utils.helper import format_fields

FIELDS = ['address', 'validator_id', 'amount', 'delegation_period', 'created', 'info']


class DelegationController(BaseContract):
    """Wrapper for DelegationController.sol functions"""

    @format_fields(FIELDS)
    def get_delegation(self, delegation_id: int) -> dict:
        """Returns delegation structure.

        :returns: Info about delegation request
        :rtype: dict
        """
        return self.__raw_get_delegation(delegation_id)

    def __raw_get_delegation(self, delegation_id: int) -> list:
        """Returns raw delegation fields.

        :returns: Info about delegation request
        :rtype: list
        """
        return self.contract.functions.getDelegation(delegation_id).call()
