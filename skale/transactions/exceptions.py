from web3.exceptions import SolidityError


class TransactionError(Exception):
    pass


class DryRunFailedError(TransactionError):
    pass


class InsufficientBalanceError(TransactionError):
    pass


class TransactionNotSentError(TransactionError):
    pass


class TransactionNotMinedError(TimeoutError, TransactionError):
    pass


class TransactionFailedError(TransactionError):
    pass


class RevertError(TransactionError, SolidityError):
    pass
