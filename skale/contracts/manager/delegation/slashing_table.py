from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes


class SlashingTable(BaseContract):
    """ Wrapper for SlashingTable.sol functions """

    @transaction_method
    def set_penalty(self, offense, penalty) -> TxRes:
        """ Set slashing penalty
        :param offense: reason of slashing
        :type offense: str
        :param penalty: penalty value to set
        :type penalty: int
        :rtype: TxRes
        """
        return self.contract.functions.setPenalty(offense, penalty)

    def get_penalty(self, offense) -> int:
        """ Get slashing penalty value
        :param offense: reason of slashing
        :type offense: str
        :rtype: int
        """
        return self.contract.functions.getPenalty(offense).call()

    @transaction_method
    def grant_role(self, role: bytes, address: str) -> TxRes:
        return self.contract.functions.grantRole(role, address)

    def penalty_setter_role(self) -> bytes:
        return self.contract.functions.PENALTY_SETTER_ROLE().call()

    def has_role(self, role: bytes, address: str) -> bool:
        return self.contract.functions.hasRole(role, address).call()
