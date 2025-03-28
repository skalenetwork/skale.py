from web3.exceptions import ContractLogicError


class TransactionError(Exception):
    """
    Base exception for transaction related errors
    """

    pass


class ChainIdError(TransactionError):
    """
    Raised when chainId is missing or incorrect
    """

    pass


class TransactionNotSignedError(TransactionError):
    """
    Raised when transaction wasn't signed
    """

    pass


class TransactionNotSentError(TransactionError):
    """
    Raised when transaction wasn't sent
    """

    pass


class TransactionNotMinedError(TimeoutError, TransactionError):
    """
    Raised when transaction wasn't included in block within timeout
    """

    pass


class TransactionWaitError(TimeoutError, TransactionError):
    """
    Raised when error occurred during waiting for transaction
    to be included in block
    """

    pass


class TransactionLogicError(TransactionError, ContractLogicError):
    """
    Raised when transaction executed with error
    """

    pass


class DryRunFailedError(TransactionLogicError):
    """
    Raised when error occurred during dry run call
    """

    pass


class TransactionFailedError(TransactionLogicError):
    """
    Raised when transaction included in the block failed during execution
    """

    pass


class TransactionRevertError(TransactionFailedError):
    """
    Raised when transaction included in the block failed with revert
    """

    pass


class DryRunRevertError(DryRunFailedError):
    """
    Raised when transaction reverted during dry run call
    """

    pass
