from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes
from skale.utils.constants import GAS


class SlashingTable(BaseContract):
    """ Wrapper for SlashingTable.sol functions """

    @transaction_method(gas_limit=GAS['set_penalty'])
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
