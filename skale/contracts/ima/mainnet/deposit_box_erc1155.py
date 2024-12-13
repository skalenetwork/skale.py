from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes


class DepositBoxERC1155(BaseContract):
    """Class deposit"""

    @transaction_method
    def add_erc1155_token(self, schain_name: str, address: int) -> TxRes:
        return self.contract.functions.addERC1155TokenByOwner(schain_name, address)

    @transaction_method
    def deposit_erc1155(
        self, schain_name: str, address: int, token_id: int, amount: int
    ) -> TxRes:
        """Deposit ERC1155"""
        return self.contract.functions.depositERC1155(
            schain_name, address, token_id, amount
        )

    @transaction_method
    def deposit_direct_erc1155(
        self, schain_name: str, address: int, token_id: int, amount: int, receiver: int
    ) -> TxRes:
        """Direct deposit ERC1155"""
        return self.contract.functions.depositERC1155Direct(
            schain_name, address, token_id, amount, receiver
        )

    @transaction_method
    def deposit_erc1155_batch(
        self, schain_name: str, address: int, ids: list, amount: list
    ) -> TxRes:
        return self.contract.functions.depositERC1155Batch(
            schain_name, address, ids, amount
        )

    def get_schain_to_erc1155(self, schain_name: str, token_address: int) -> bool:
        return self.contract.functions.getSchainToERC1155(schain_name, token_address).call()
