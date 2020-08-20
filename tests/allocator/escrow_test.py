""" Tests for skale/allocator/escrow.py """

from tests.constants import (D_DELEGATION_INFO, D_VALIDATOR_ID,
                             D_DELEGATION_AMOUNT, D_DELEGATION_PERIOD)


# @pytest.mark.skip(reason="not ready yet")
def test_delegate(skale_allocator):
    skale_allocator.escrow.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True
    )
