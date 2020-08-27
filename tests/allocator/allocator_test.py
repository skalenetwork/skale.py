""" Tests for skale/allocator/allocator.py """

from skale.wallets.web3_wallet import generate_wallet
from skale.utils.account_tools import send_ether

from skale.utils.contracts_provision import D_PLAN_ID
from skale.utils.contracts_provision.allocator import add_test_plan, connect_test_beneficiary


def test_is_beneficiary_registered(skale_allocator):
    wallet = generate_wallet(skale_allocator.web3)
    assert not skale_allocator.allocator.is_beneficiary_registered(wallet.address)


def test_add_plan(skale_allocator):
    plan_id = add_test_plan(skale_allocator)
    assert isinstance(plan_id, int)


def test_connect_beneficiary_to_plan(skale_allocator):
    wallet = generate_wallet(skale_allocator.web3)
    assert not skale_allocator.allocator.is_beneficiary_registered(wallet.address)
    connect_test_beneficiary(skale_allocator, D_PLAN_ID, wallet)
    assert skale_allocator.allocator.is_beneficiary_registered(wallet.address)


def test_start_vesting(skale_allocator):
    main_wallet = skale_allocator.wallet
    wallet = generate_wallet(skale_allocator.web3)

    connect_test_beneficiary(skale_allocator, D_PLAN_ID, wallet)
    send_ether(skale_allocator.web3, main_wallet, wallet.address, 0.1)

    assert skale_allocator.allocator.is_delegation_allowed(wallet.address)

    assert not skale_allocator.allocator.is_vesting_active(wallet.address)
    skale_allocator.allocator.start_vesting(wallet.address, wait_for=True)
    assert skale_allocator.allocator.is_vesting_active(wallet.address)
