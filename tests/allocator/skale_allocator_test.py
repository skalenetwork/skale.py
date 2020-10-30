""" SKALE Allocator test """

from skale import SkaleAllocator
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.skale_allocator import CONTRACTS_INFO, spawn_skale_allocator_from
from tests.constants import ENDPOINT, TEST_ALLOCATOR_ABI_FILEPATH, ETH_PRIVATE_KEY


def test_init_allocator():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    skale_allocator = SkaleAllocator(ENDPOINT, TEST_ALLOCATOR_ABI_FILEPATH, wallet,
                                     provider_timeout=20)
    lib_contracts = skale_allocator._SkaleBase__contracts
    assert len(lib_contracts) == len(CONTRACTS_INFO)

    assert skale_allocator.allocator
    assert skale_allocator.escrow


def test_spawn_skale_allocator_from():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    provider_timeout = 20
    allocator = SkaleAllocator(ENDPOINT, TEST_ALLOCATOR_ABI_FILEPATH, wallet,
                               provider_timeout=provider_timeout)
    new_allocator = spawn_skale_allocator_from(allocator)
    assert allocator.wallet is new_allocator.wallet
    assert allocator._provider_timeout == provider_timeout
    lib_contracts = allocator._SkaleBase__contracts
    new_lib_contracts = new_allocator._SkaleBase__contracts
    assert len(lib_contracts) == len(new_lib_contracts)

    assert allocator.allocator and allocator.escrow
    assert new_allocator.allocator and new_allocator.escrow

    new_wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    new_provider_timeout = 30
    new_manager = spawn_skale_allocator_from(
        allocator, wallet=new_wallet, provider_timeout=new_provider_timeout)

    assert new_manager.wallet is new_wallet
    assert new_manager._provider_timeout == new_provider_timeout
