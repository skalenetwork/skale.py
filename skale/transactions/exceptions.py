from web3.exceptions import ContractLogicError


class TransactionError(Exception):
    pass


class TransactionNotSentError(TransactionError):
    pass


class TransactionNotMinedError(TimeoutError, TransactionError):
    pass


class TransactionWaitError(TimeoutError, TransactionError):
    pass


class TransactionLogicError(TransactionError):
    pass


class DryRunFailedError(TransactionLogicError):
    pass


class TransactionFailedError(TransactionLogicError):
    pass


class RevertError(TransactionLogicError):
    pass
