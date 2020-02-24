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

from skale.contracts import BaseContract, transaction_method
from skale.utils.helper import format_fields

from skale.transactions.tools import post_transaction
from skale.dataclasses.tx_res import TxRes
from skale.utils.constants import GAS

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

    def get_with_id(self, _id) -> dict:
        """Returns validator info with ID.

        :returns: Validator info with ID
        :rtype: dict
        """
        validator = self.get(_id)
        validator['id'] = _id
        return validator

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
        number_of_validators = self.number_of_validators()
        validators = [
            self.get_with_id(val_id)
            for val_id in range(1, number_of_validators+1)
        ]
        return validators

    def get_linked_addresses_by_validator_address(self, address: str) -> list:
        """Returns list of node addresses linked to the validator address.

        :returns: List of node addresses
        :rtype: list
        """
        return self.contract.functions.getMyAddresses().call({
            'from': address
        })

    def get_linked_addresses_by_validator_id(self, validator_id: str) -> list:
        """Returns list of node addresses linked to the validator ID.

        :returns: List of node addresses
        :rtype: list
        """
        return self.contract.functions.getValidatorAddresses(validator_id).call()

    def is_main_address(self, validator_address: str) -> bool:
        """Checks if provided address is the main validator address

        :returns: True if provided address is the main validator address, otherwise False
        :rtype: bool
        """
        validator_id = self.validator_id_by_address(validator_address)
        validator = self.get(validator_id)
        return validator_address == validator['validator_address']

    def validator_address_exists(self, validator_address: str) -> bool:
        """Checks if there is a validator with provided address

        :returns: True if validator exists, otherwise False
        :rtype: bool
        """
        return self.contract.functions.validatorAddressExists(validator_address).call()

    def validator_id_by_address(self, validator_address: str) -> int:
        """Returns validator ID by validator address

        :returns: Validator ID
        :rtype: int
        """
        return self.contract.functions.getValidatorId(validator_address).call()

    @transaction_method
    def _enable_validator(self, validator_id: int) -> TxRes:
        """For internal usage only"""
        func = self.contract.functions.enableValidator(validator_id)
        return post_transaction(self.skale.wallet, func, GAS['enable_validator'])

    def _is_validator_trusted(self, validator_id: int) -> bool:
        """For internal usage only"""
        return self.contract.functions.trustedValidators(validator_id).call()
