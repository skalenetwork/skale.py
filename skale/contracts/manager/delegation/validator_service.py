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

from typing import Any, Dict, List
from eth_typing import ChecksumAddress
from web3 import Web3
from web3.contract.contract import ContractFunction
from web3.types import Wei, HexBytes

from skale.contracts.base_contract import transaction_method
from skale.contracts.skale_manager_contract import SkaleManagerContract
from skale.types.validator import Validator, ValidatorId, ValidatorWithId
from skale.utils.helper import format_fields


FIELDS = [
    'name',
    'validator_address',
    'requested_address',
    'description',
    'fee_rate',
    'registration_time',
    'minimum_delegation_amount',
    'accept_new_requests',
    'trusted',
]


class ValidatorService(SkaleManagerContract):
    """Wrapper for ValidatorService.sol functions"""

    def __get_raw(self, _id: ValidatorId) -> List[Any]:
        """Returns raw validator info.

        :returns: Raw validator info
        :rtype: list
        """
        return list(self.contract.functions.validators(_id).call())

    @format_fields(FIELDS)
    def untyped_get(self, _id: ValidatorId) -> List[Any]:
        """Returns validator info.

        :returns: Validator info
        :rtype: dict
        """
        validator = self.__get_raw(_id)
        trusted = self._is_authorized_validator(_id)
        validator.append(trusted)
        return validator

    def get(self, _id: ValidatorId) -> Validator:
        untyped_validator = self.untyped_get(_id)
        if untyped_validator is None:
            raise ValueError('Validator with id ', _id, ' is missing')
        if isinstance(untyped_validator, dict):
            return self._to_validator(untyped_validator)
        if isinstance(untyped_validator, list):
            return self._to_validator(untyped_validator[0])
        raise TypeError(_id)

    def get_with_id(self, _id: ValidatorId) -> ValidatorWithId:
        """Returns validator info with ID.

        :returns: Validator info with ID
        :rtype: dict
        """
        validator = self.get(_id)
        return ValidatorWithId({'id': _id, **validator})

    def number_of_validators(self) -> int:
        """Returns number of registered validators.

        :returns: List of validators
        :rtype: int
        """
        return int(self.contract.functions.numberOfValidators().call())

    def ls(self, trusted_only: bool = False) -> List[ValidatorWithId]:
        """Returns list of registered validators.

        :returns: List of validators
        :rtype: list
        """
        number_of_validators = self.number_of_validators()
        validators = (
            [self.get_with_id(val_id) for val_id in self.get_trusted_validator_ids()]
            if trusted_only
            else [
                self.get_with_id(ValidatorId(val_id))
                for val_id in range(1, number_of_validators + 1)
            ]
        )
        return validators

    def get_linked_addresses_by_validator_address(
        self, address: ChecksumAddress
    ) -> List[ChecksumAddress]:
        """Returns list of node addresses linked to the validator address.

        :returns: List of node addresses
        :rtype: list
        """
        return [
            Web3.to_checksum_address(address)
            for address in self.contract.functions.getMyNodesAddresses().call({'from': address})
        ]

    def get_linked_addresses_by_validator_id(
        self, validator_id: ValidatorId
    ) -> List[ChecksumAddress]:
        """Returns list of node addresses linked to the validator ID.

        :returns: List of node addresses
        :rtype: list
        """
        return [
            Web3.to_checksum_address(address)
            for address in self.contract.functions.getNodeAddresses(validator_id).call()
        ]

    def is_main_address(self, validator_address: ChecksumAddress) -> bool:
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

    def validator_address_exists(self, validator_address: ChecksumAddress) -> bool:
        """Checks if there is a validator with provided address

        :returns: True if validator exists, otherwise False
        :rtype: bool
        """
        return bool(self.contract.functions.validatorAddressExists(validator_address).call())

    def validator_exists(self, validator_id: ValidatorId) -> bool:
        """Checks if there is a validator with provided ID

        :returns: True if validator exists, otherwise False
        :rtype: bool
        """
        return bool(self.contract.functions.validatorExists(validator_id).call())

    def validator_id_by_address(self, validator_address: ChecksumAddress) -> ValidatorId:
        """Returns validator ID by validator address

        :returns: Validator ID
        :rtype: int
        """
        return ValidatorId(self.contract.functions.getValidatorId(validator_address).call())

    def get_trusted_validator_ids(self) -> List[ValidatorId]:
        """Returns list of trusted validators id.

        :returns: List of trusted validators id
        :rtype: list
        """
        return [ValidatorId(id) for id in self.contract.functions.getTrustedValidators().call()]

    @transaction_method
    def _enable_validator(self, validator_id: ValidatorId) -> 'ContractFunction':
        """For internal usage only"""
        return self.contract.functions.enableValidator(validator_id)

    @transaction_method
    def _disable_validator(self, validator_id: ValidatorId) -> 'ContractFunction':
        """For internal usage only"""
        return self.contract.functions.disableValidator(validator_id)

    def _is_authorized_validator(self, validator_id: ValidatorId) -> bool:
        """For internal usage only"""
        return bool(self.contract.functions.isAuthorizedValidator(validator_id).call())

    def is_accepting_new_requests(self, validator_id: ValidatorId) -> bool:
        """For internal usage only"""
        return bool(self.contract.functions.isAcceptingNewRequests(validator_id).call())

    @transaction_method
    def register_validator(
        self, name: str, description: str, fee_rate: int, min_delegation_amount: int
    ) -> 'ContractFunction':
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
            name, description, fee_rate, min_delegation_amount
        )

    def get_link_node_signature(self, validator_id: ValidatorId) -> HexBytes:
        unsigned_hash = Web3.solidity_keccak(['uint256'], [validator_id])
        signed_hash = self.skale.wallet.sign_hash(unsigned_hash.hex())
        return signed_hash.signature

    @transaction_method
    def link_node_address(
        self, node_address: ChecksumAddress, signature: HexBytes
    ) -> 'ContractFunction':
        """Link node address to your validator account.

        :param node_address: Address of the node to link
        :type node_address: str
        :param signature: Signature - result of the get_link_node_signature function
        :type signature: HexBytes
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.linkNodeAddress(node_address, signature)

    @transaction_method
    def unlink_node_address(self, node_address: ChecksumAddress) -> 'ContractFunction':
        """Unlink node address from your validator account.

        :param node_address: Address of the node to unlink
        :type node_address: str
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.unlinkNodeAddress(node_address)

    @transaction_method
    def disable_whitelist(self) -> 'ContractFunction':
        """Disable validator whitelist. Master key only transaction.
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.disableWhitelist()

    def get_use_whitelist(self) -> bool:
        """Return useWhitelist contract variable
        :returns: useWhitelist value
        :rtype: bool
        """
        return bool(self.contract.functions.useWhitelist().call())

    def get_and_update_bond_amount(self, validator_id: ValidatorId) -> int:
        """Return amount of token that validator delegated to himself
        :param validator_id: id of the validator
        :returns:
        :rtype: int
        """
        return int(self.contract.functions.getAndUpdateBondAmount(validator_id).call())

    @transaction_method
    def set_validator_mda(self, minimum_delegation_amount: Wei) -> 'ContractFunction':
        """Allows a validator to set the minimum delegation amount.

        :param new_minimum_delegation_amount: Minimum delegation amount
        :type new_minimum_delegation_amount: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.setValidatorMDA(minimum_delegation_amount)

    @transaction_method
    def request_for_new_address(self, new_validator_address: ChecksumAddress) -> 'ContractFunction':
        """Allows a validator to request a new address.

        :param new_validator_address: New validator address
        :type new_validator_address: str
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.requestForNewAddress(new_validator_address)

    @transaction_method
    def confirm_new_address(self, validator_id: ValidatorId) -> 'ContractFunction':
        """Confirm change of the address.

        :param validator_id: ID of the validator
        :type validator_id: int
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.confirmNewAddress(validator_id)

    @transaction_method
    def set_validator_name(self, new_name: str) -> 'ContractFunction':
        """Allows a validator to change the name.

        :param new_name: New validator name
        :type new_name: str
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.setValidatorName(new_name)

    @transaction_method
    def set_validator_description(self, new_description: str) -> 'ContractFunction':
        """Allows a validator to change the name.

        :param new_description: New validator description
        :type new_name: str
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.setValidatorDescription(new_description)

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> 'ContractFunction':
        return self.contract.functions.grantRole(role, address)

    def validator_manager_role(self) -> bytes:
        return bytes(self.contract.functions.VALIDATOR_MANAGER_ROLE().call())

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.hasRole(role, address).call())

    def _to_validator(self, untyped_validator: Dict[str, Any]) -> Validator:
        return Validator(
            {
                'name': str(untyped_validator['name']),
                'validator_address': ChecksumAddress(untyped_validator['validator_address']),
                'requested_address': ChecksumAddress(untyped_validator['requested_address']),
                'description': str(untyped_validator['description']),
                'fee_rate': int(untyped_validator['fee_rate']),
                'registration_time': int(untyped_validator['registration_time']),
                'minimum_delegation_amount': Wei(untyped_validator['minimum_delegation_amount']),
                'accept_new_requests': bool(untyped_validator['accept_new_requests']),
                'trusted': bool(untyped_validator['trusted']),
            }
        )
