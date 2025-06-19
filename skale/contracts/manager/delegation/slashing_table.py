from eth_typing import ChecksumAddress
from web3.contract.contract import ContractFunction
from web3.types import Wei

from skale.contracts.base_contract import transaction_method
from skale.contracts.skale_manager_contract import SkaleManagerContract


class SlashingTable(SkaleManagerContract):
    """Wrapper for SlashingTable.sol functions"""

    @transaction_method
    def set_penalty(self, offense: str, penalty: Wei) -> 'ContractFunction':
        """Set slashing penalty
        :param offense: reason of slashing
        :type offense: str
        :param penalty: penalty value to set
        :type penalty: int
        :rtype: TxRes
        """
        return self.contract.functions.setPenalty(offense, penalty)

    def get_penalty(self, offense: str) -> Wei:
        """Get slashing penalty value
        :param offense: reason of slashing
        :type offense: str
        :rtype: int
        """
        return Wei(self.contract.functions.getPenalty(offense).call())

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> 'ContractFunction':
        return self.contract.functions.grantRole(role, address)

    def penalty_setter_role(self) -> bytes:
        return bytes(self.contract.functions.PENALTY_SETTER_ROLE().call())

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.hasRole(role, address).call())
