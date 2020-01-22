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


FIELDS = [
    'name', 'validator_address', 'requested_address', 'description', 'fee_rate',
    'registration_time', 'minimum_delegation_amount', 'last_bounty_collection_month'
]


class ValidatorService(BaseContract):
    """Wrapper for ValidatorService.sol functions"""

    def __get_raw(self, _id) -> list:
        """Returns raw validator info.

        :returns: Raw validator info
        :rtype: list
        """
        return self.contract.functions.validators(_id).call()

    @format_fields(FIELDS)
    def get(self, _id) -> dict:
        """Returns validator info.

        :returns: Validator info
        :rtype: dict
        """
        return self.__get_raw(_id)

    def number_of_validators(self):
        """Returns number of registered validators.

        :returns: List of validators
        :rtype: int
        """
        return self.contract.functions.numberOfValidators().call()

    def ls(self):
        """Returns list of registered validators.

        :returns: List of validators
        :rtype: list
        """
        validators = []
        number_of_validators = self.number_of_validators()
        for val_id in range(1, number_of_validators+1):
            val = self.get(val_id)
            val['id'] = val_id
            validators.append(val)
        return validators
