""" Tests for skale/allocator/core_escrow.py """

import pytest
from tests.constants import (D_DELEGATION_INFO, D_VALIDATOR_ID,
                             D_DELEGATION_AMOUNT, D_DELEGATION_PERIOD)


@pytest.mark.skip(reason="not ready yet")
def test_delegate(skale_allocator):
    skale_allocator.core_escrow.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True
    )
