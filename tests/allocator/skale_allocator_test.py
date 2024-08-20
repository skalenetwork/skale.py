""" SKALE Allocator test """

from skale import SkaleAllocator
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from tests.constants import ENDPOINT, TEST_ALLOCATOR_ABI_FILEPATH, ETH_PRIVATE_KEY


def test_init_allocator():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    skale_allocator = SkaleAllocator(ENDPOINT, TEST_ALLOCATOR_ABI_FILEPATH, wallet,
                                     provider_timeout=20)
    assert len(skale_allocator._SkaleBase__contracts) == 1
    assert skale_allocator.allocator
    assert skale_allocator.escrow
    assert len(skale_allocator._SkaleBase__contracts) == 3
