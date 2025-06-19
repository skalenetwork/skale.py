"""SKALE Allocator test"""

from functools import cached_property
from skale import SkaleAllocator
from skale.utils.helper import get_allocator_address
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from tests.constants import ENDPOINT, TEST_ALLOCATOR_ABI_FILEPATH, ETH_PRIVATE_KEY

ALLOCATOR_CONTRACTS_NUMBER = 2


def test_init_allocator():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    skale_allocator = SkaleAllocator(
        ENDPOINT, get_allocator_address(TEST_ALLOCATOR_ABI_FILEPATH), wallet, provider_timeout=20
    )
    cached_properties = [
        attr
        for attr in dir(skale_allocator)
        if isinstance(getattr(type(skale_allocator), attr, None), cached_property)
    ]

    assert len(cached_properties) == ALLOCATOR_CONTRACTS_NUMBER
    assert skale_allocator.allocator
    assert skale_allocator.escrow
