from web3.exceptions import TransactionNotFound as Web3TransactionNotFoundError


class TransactionError(Exception):
    pass


class DryRunFailedError(TransactionError):
    pass


class InsufficientBalanceError(TransactionError):
    pass


class TransactionFailedError(TransactionError):
    pass


class TransactionNotFoundError(TransactionError, Web3TransactionNotFoundError):
    pass
