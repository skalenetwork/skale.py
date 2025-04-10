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

from skale.contracts.base_contract import BaseContract, transaction_method
from eth_typing import ChecksumAddress
from skale.transactions.result import TxRes


class ConfigController(BaseContract):
    """Config controller contract"""

    def default_admin_role(self) -> bytes:
        return self.contract.functions.DEFAULT_ADMIN_ROLE().call()

    def deployer_admin_role(self) -> bytes:
        return self.contract.functions.DEPLOYER_ADMIN_ROLE().call()

    def deployer_role(self) -> bytes:
        return self.contract.functions.DEPLOYER_ROLE().call()

    def mtm_admin_role(self) -> bytes:
        return self.contract.functions.MTM_ADMIN_ROLE().call()

    def allowed_origin_role(self, deployer: ChecksumAddress) -> bytes:
        return self.contract.functions.allowedOriginRole(deployer).call()

    def allowed_origin_role_admin(self, deployer: ChecksumAddress) -> bytes:
        return self.contract.functions.allowedOriginRoleAdmin(deployer).call()

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.hasRole(role, address).call())

    def get_role_admin(self, role: bytes) -> bytes:
        return self.contract.functions.getRoleAdmin(role).call()

    def get_role_member(self, role: bytes, index: int) -> bytes:
        return self.contract.functions.getRoleMember(role, index).call()

    def get_role_member_count(self, role: bytes) -> int:
        return self.contract.functions.getRoleMemberCount(role).call()

    def is_address_whitelisted(self, address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.isAddressWhitelisted(address).call())

    def is_deployment_allowed(
        self, transaction_origin: ChecksumAddress, deployer: ChecksumAddress
    ) -> bool:
        return bool(
            self.contract.functions.isDeploymentAllowed(transaction_origin, deployer).call()
        )

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.grantRole(role, address)

    @transaction_method
    def add_allowed_origin_role_admin(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.addAllowedOriginRoleAdmin(role, address)

    @transaction_method
    def allow_origin(self, transaction_origin: ChecksumAddress, deployer: ChecksumAddress) -> TxRes:
        return self.contract.functions.allowOrigin(transaction_origin, deployer)

    @transaction_method
    def add_to_whitelist(self, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.addToWhitelist(address)

    @transaction_method
    def revoke_role(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.revokeRole(role, address)

    @transaction_method
    def renounce_role(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.renounceRole(role, address)

    @transaction_method
    def remove_allowed_origin_role_admin(self, role: bytes, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.removeAllowedOriginRoleAdmin(role, address)

    @transaction_method
    def forbid_origin(
        self, transaction_origin: ChecksumAddress, deployer: ChecksumAddress
    ) -> TxRes:
        return self.contract.functions.forbidOrigin(transaction_origin, deployer)

    @transaction_method
    def remove_from_whitelist(self, address: ChecksumAddress) -> TxRes:
        return self.contract.functions.removeFromWhitelist(address)

    @transaction_method
    def enable_free_contract_deployment(self) -> TxRes:
        return self.contract.functions.enableFreeContractDeployment()

    @transaction_method
    def disable_free_contract_deployment(self) -> TxRes:
        return self.contract.functions.disableFreeContractDeployment()

    def is_fcd_enabled(self) -> str:
        return self.contract.functions.isFCDEnabled().call()

    @transaction_method
    def enable_mtm(self) -> TxRes:
        return self.contract.functions.enableMTM()

    @transaction_method
    def disable_mtm(self) -> TxRes:
        return self.contract.functions.disableMTM()

    def is_mtm_enabled(self) -> str:
        return self.contract.functions.isMTMEnabled().call()

    def get_version(self) -> str:
        return self.contract.functions.version().call()

    @transaction_method
    def set_version(self, new_version) -> TxRes:
        return self.contract.functions.setVersion(new_version)
