from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes
from eth_typing import ChecksumAddress
from web3.contract.contract import ContractFunction


class ConfigController(BaseContract):
    """Config controller contract"""

    def default_admin_role(self) -> hex:
        return "0x" + self.contract.functions.DEFAULT_ADMIN_ROLE().call().hex()

    def deployer_admin_role(self) -> hex:
        return "0x" + self.contract.functions.DEPLOYER_ADMIN_ROLE().call().hex()

    def deployer_role(self) -> hex:
        return "0x" + self.contract.functions.DEPLOYER_ROLE().call().hex()

    def mtm_admin_role(self) -> hex:
        return "0x" + self.contract.functions.MTM_ADMIN_ROLE().call().hex()

    def allowed_origin_role(self, deployer: ChecksumAddress) -> hex:
        return "0x" + self.contract.functions.allowedOriginRole(deployer).call().hex()

    def allowed_origin_role_admin(self, deployer: ChecksumAddress) -> hex:
        return "0x" + self.contract.functions.allowedOriginRoleAdmin(deployer).call().hex()

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.hasRole(role, address).call())

    def get_role_admin(self, role: bytes) -> hex:
        return self.contract.functions.getRoleAdmin(role).call().hex()

    def get_role_member(self, role: bytes, index: int) -> bytes:
        return self.contract.functions.getRoleMember(role, index).call()

    def get_role_member_count(self, role: bytes) -> int:
        return self.contract.functions.getRoleMemberCount(role).call()

    def is_address_whitelisted(self, address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.isAddressWhitelisted(address).call())

    def is_deployment_allowed(self, transactionOrigin: ChecksumAddress, deployer: ChecksumAddress) -> bool:
        return bool(self.contract.functions.isDeploymentAllowed(transactionOrigin, deployer).call())

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.grantRole(role, address)

    @transaction_method
    def add_allowed_origin_role_admin(self, role: bytes, address: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.addAllowedOriginRoleAdmin(role, address)

    @transaction_method
    def allow_origin(self, transactionOrigin: ChecksumAddress, deployer: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.allowOrigin(transactionOrigin, deployer)

    @transaction_method
    def add_to_whitelist(self, address: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.addToWhitelist(address)

    @transaction_method
    def revoke_role(self, role: bytes, address: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.revokeRole(role, address)

    @transaction_method
    def renounce_role(self, role: bytes, address: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.renounceRole(role, address)

    @transaction_method
    def remove_allowed_origin_role_admin(self, role: bytes, address: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.removeAllowedOriginRoleAdmin(role, address)

    @transaction_method
    def forbid_origin(self, transactionOrigin: ChecksumAddress, deployer: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.forbidOrigin(transactionOrigin, deployer)

    @transaction_method
    def remove_from_whitelist(self, address: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.removeFromWhitelist(address)
    
    @transaction_method
    def enable_free_contract_deployment(self) -> ContractFunction:
        return self.contract.functions.enableFreeContractDeployment()

    @transaction_method
    def disable_free_contract_deployment(self) -> ContractFunction:
        return self.contract.functions.disableFreeContractDeployment()

    def is_fcd_enabled(self) -> str:
        return self.contract.functions.isFCDEnabled().call()

    @transaction_method
    def enable_mtm(self) -> ContractFunction:
        return self.contract.functions.enableMTM()

    @transaction_method
    def disable_mtm(self) -> ContractFunction:
        return self.contract.functions.disableMTM()

    def is_mtm_enabled(self) -> str:
        return self.contract.functions.isMTMEnabled().call()

    def get_version(self) -> str:
        return self.contract.functions.version().call()

    @transaction_method
    def set_version(self, new_version) -> ContractFunction:
        return self.contract.functions.setVersion(new_version)
        