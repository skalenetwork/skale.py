""" SKALE data prep for testing """

from skale import SkaleAllocator
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.utils.helper import init_default_logger
from tests.constants import ENDPOINT, TEST_ABI_FILEPATH, ETH_PRIVATE_KEY


def prepare_data():
    init_default_logger()
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    return SkaleAllocator(ENDPOINT, TEST_ABI_FILEPATH, wallet)


if __name__ == "__main__":
    prepare_data()
