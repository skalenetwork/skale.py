from skale.contracts.base_contract import BaseContract, transaction_method
from eth_typing import ChecksumAddress
from skale.transactions.result import TxRes


class Context(BaseContract):
    """Context contract"""

    def get_schain_name(self) -> str:
        return self.contract.functions.getSchainName().call()

    def get_schain_owner_address(self) -> bytes:
        return self.contract.functions.getSchainOwnerAddress().call()

    @transaction_method
    def set_schain_owner_address(self, newOwner: ChecksumAddress) -> TxRes:
        return self.contract.functions.setSchainOwnerAddress(newOwner)

    def get_version(self) -> str:
        return self.contract.functions.version().call()
