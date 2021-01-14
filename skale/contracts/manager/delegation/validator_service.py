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

from web3 import Web3

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.utils.helper import format_fields

from skale.transactions.result import TxRes


FIELDS = [
    'name', 'validator_address', 'requested_address', 'description', 'fee_rate',
    'registration_time', 'minimum_delegation_amount', 'accept_new_requests',
    'trusted'
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
        validator = self.__get_raw(_id)
        trusted = self._is_authorized_validator(_id)
        validator.append(trusted)
        return validator

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

    def ls(self, trusted_only=False):
        """Returns list of registered validators.

        :returns: List of validators
        :rtype: list
        """
        number_of_validators = self.number_of_validators()
        validators = [
            self.get_with_id(val_id)
            for val_id in self.get_trusted_validator_ids()
        ] if trusted_only else [
            self.get_with_id(val_id)
            for val_id in range(1, number_of_validators + 1)
        ]
        return validators

    def get_linked_addresses_by_validator_address(self, address: str) -> list:
        """Returns list of node addresses linked to the validator address.

        :returns: List of node addresses
        :rtype: list
        """
        return self.contract.functions.getMyNodesAddresses().call({
            'from': address
        })

    def get_linked_addresses_by_validator_id(self, validator_id: int) -> list:
        """Returns list of node addresses linked to the validator ID.

        :returns: List of node addresses
        :rtype: list
        """
        return self.contract.functions.getNodeAddresses(validator_id).call()

    def is_main_address(self, validator_address: str) -> bool:
        """Checks if provided address is the main validator address

        :returns: True if provided address is the main validator address, otherwise False
        :rtype: bool
        """
        if not self.validator_address_exists(validator_address):
            return False

        try:
            # TODO: handle address that is not main in a proper way
            validator_id = self.validator_id_by_address(validator_address)
            validator = self.get(validator_id)
        except Exception:
            return False

        return validator_address == validator['validator_address']

    def validator_address_exists(self, validator_address: str) -> bool:
        """Checks if there is a validator with provided address

        :returns: True if validator exists, otherwise False
        :rtype: bool
        """
        return self.contract.functions.validatorAddressExists(validator_address).call()

    def validator_exists(self, validator_id: str) -> bool:
        """Checks if there is a validator with provided ID

        :returns: True if validator exists, otherwise False
        :rtype: bool
        """
        return self.contract.functions.validatorExists(validator_id).call()

    def validator_id_by_address(self, validator_address: str) -> int:
        """Returns validator ID by validator address

        :returns: Validator ID
        :rtype: int
        """
        return self.contract.functions.getValidatorId(validator_address).call()

    def get_trusted_validator_ids(self) -> list:
        """Returns list of trusted validators id.

        :returns: List of trusted validators id
        :rtype: list
        """
        return self.contract.functions.getTrustedValidators().call()

    @transaction_method
    def _enable_validator(self, validator_id: int) -> TxRes:
        """For internal usage only"""
        return self.contract.functions.enableValidator(validator_id)

    @transaction_method
    def _disable_validator(self, validator_id: int) -> TxRes:
        """For internal usage only"""
        return self.contract.functions.disableValidator(validator_id)

    def _is_authorized_validator(self, validator_id: int) -> bool:
        """For internal usage only"""
        return self.contract.functions.isAuthorizedValidator(validator_id).call()

    def is_accepting_new_requests(self, validator_id: int) -> bool:
        """For internal usage only"""
        return self.contract.functions.isAcceptingNewRequests(validator_id).call()

    @transaction_method
    def register_validator(self, name: str, description: str, fee_rate: int,
                           min_delegation_amount: int) -> TxRes:
        """Registers a new validator in the SKALE Manager contracts.

        :param name: Validator name
        :type name: str
        :param description: Validator description
        :type description: str
        :param fee_rate: Validator fee rate
        :type fee_rate: int
        :param min_delegation_amount: Minimal delegation amount
        :type min_delegation_amount: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.registerValidator(
            name, description, fee_rate, min_delegation_amount)

    def get_link_node_signature(self, validator_id: int) -> str:
        unsigned_hash = Web3.soliditySha3(['uint256'], [validator_id])
        signed_hash = self.skale.wallet.sign_hash(unsigned_hash.hex())
        return signed_hash.signature.hex()

    @transaction_method
    def link_node_address(self, node_address: str, signature: str) -> TxRes:
        """Link node address to your validator account.

        :param node_address: Address of the node to link
        :type node_address: str
        :param signature: Signature - reuslt of the get_link_node_signature function
        :type signature: str
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.linkNodeAddress(node_address, signature)

    @transaction_method
    def unlink_node_address(self, node_address: str) -> TxRes:
        """Unlink node address from your validator account.

        :param node_address: Address of the node to unlink
        :type node_address: str
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.unlinkNodeAddress(node_address)

    @transaction_method
    def disable_whitelist(self) -> TxRes:
        """ Disable validator whitelist. Master key only transaction.
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.disableWhitelist()

    def get_use_whitelist(self) -> bool:
        """ Return useWhitelist contract variable
        :returns: useWhitelist value
        :rtype: bool
        """
        return self.contract.functions.useWhitelist().call()

    def get_and_update_bond_amount(self, validator_id: int) -> int:
        """Return amount of token that validator delegated to himself
           :param validator_id: id of the validator
           :returns:
           :rtype: int
        """
        return self.contract.functions.getAndUpdateBondAmount(validator_id).call()

    @transaction_method
    def set_validator_mda(self, minimum_delegation_amount: int) -> TxRes:
        """ Allows a validator to set the minimum delegation amount.

        :param new_minimum_delegation_amount: Minimum delegation amount
        :type new_minimum_delegation_amount: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.setValidatorMDA(minimum_delegation_amount)

    @transaction_method
    def request_for_new_address(self, new_validator_address: str) -> TxRes:
        """ Allows a validator to request a new address.

        :param new_validator_address: New validator address
        :type new_validator_address: str
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.requestForNewAddress(new_validator_address)

    @transaction_method
    def confirm_new_address(self, validator_id: int) -> TxRes:
        """  Confirm change of the address.

        :param validator_id: ID of the validator
        :type validator_id: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.confirmNewAddress(validator_id)

    @transaction_method
    def set_validator_name(self, new_name: str) -> TxRes:
        """ Allows a validator to change the name.

        :param new_name: New validator name
        :type new_name: str
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.setValidatorName(new_name)

    @transaction_method
    def set_validator_description(self, new_description: str) -> TxRes:
        """ Allows a validator to change the name.

        :param new_description: New validator description
        :type new_name: str
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.setValidatorDescription(new_description)
