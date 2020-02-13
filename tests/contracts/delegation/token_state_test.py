""" Tests for contracts/delegation/token_state.py """

from skale.utils.web3_utils import check_receipt
from skale.dataclasses.delegation_status import DelegationStatus

from tests.constants import (
    D_VALIDATOR_ID, D_DELEGATION_AMOUNT, D_DELEGATION_PERIOD, D_DELEGATION_INFO
)


def test_skip_transition_delay(skale):
    tx_res = skale.delegation_service.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True
    )
    check_receipt(tx_res.receipt)
    delegations = skale.delegation_service.get_delegations(
        skale.wallet.address,
        DelegationStatus.PROPOSED,
        'validator'
    )
    delegation_id = delegations[-1]['id']
    tx_res = skale.delegation_service.accept_pending_delegation(
        delegation_id,
        wait_for=True
    )
    check_receipt(tx_res.receipt)

    tx_res = skale.token_state._skip_transition_delay(
        delegation_id=delegation_id,
        wait_for=True
    )
    check_receipt(tx_res.receipt)

    delegations = skale.delegation_service.get_delegations(
        skale.wallet.address,
        DelegationStatus.DELEGATED,
        'validator'
    )
    assert delegations[-1]['id'] == delegation_id
