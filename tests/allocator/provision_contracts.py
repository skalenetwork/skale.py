""" Provision Allocator contracts for testing """

from skale import SkaleAllocator, SkaleManager
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from skale.utils.helper import init_default_logger
from skale.utils.contracts_provision.allocator import transfer_tokens_to_allocator, add_test_plan

from tests.constants import (ENDPOINT, TEST_ABI_FILEPATH, ETH_PRIVATE_KEY,
                             TEST_ALLOCATOR_ABI_FILEPATH)


def init_libs():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    return (SkaleManager(ENDPOINT, TEST_ABI_FILEPATH, wallet),
            SkaleAllocator(ENDPOINT, TEST_ALLOCATOR_ABI_FILEPATH, wallet))


def provision_contracts():
    init_default_logger()
    skale_manager, skale_allocator = init_libs()

    launch_ts = skale_manager.constants_holder.get_launch_timestamp()
    if launch_ts != 0:
        skale_manager.constants_holder.set_launch_timestamp(0, wait_for=True)

    vesting_manager_role = skale_allocator.allocator.vesting_manager_role()
    skale_allocator.allocator.grant_role(vesting_manager_role, skale_allocator.wallet.address)
    transfer_tokens_to_allocator(skale_manager, skale_allocator)
    add_test_plan(skale_allocator)


if __name__ == "__main__":
    provision_contracts()
