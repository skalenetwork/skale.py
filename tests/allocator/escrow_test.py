""" Tests for skale/allocator/escrow.py """

import pytest
from skale.wallets.web3_wallet import generate_wallet
from skale.utils.account_tools import send_ether

from tests.allocator.allocator_test import _add_plan_and_connect_beneficiary
from tests.constants import (D_DELEGATION_INFO, D_VALIDATOR_ID,
                             D_DELEGATION_AMOUNT, D_DELEGATION_PERIOD)


@pytest.mark.skip(reason="not ready yet")
def test_delegate(skale_allocator):
    main_wallet = skale_allocator.wallet
    wallet = generate_wallet(skale_allocator.web3)
    send_ether(skale_allocator.web3, main_wallet, wallet.address, 0.1)
    _add_plan_and_connect_beneficiary(skale_allocator, wallet)

    skale_allocator.wallet = wallet
    skale_allocator.escrow.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True
    )
    skale_allocator.wallet = main_wallet
