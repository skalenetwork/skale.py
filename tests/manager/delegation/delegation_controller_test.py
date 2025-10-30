"""Tests for contracts/delegation/delegation_controller.py"""

import pytest

from skale.contracts.manager.delegation.delegation_controller import FIELDS
from skale.transactions.exceptions import ContractLogicError
from skale.transactions.result import DryRunRevertError
from skale.types.delegation import DelegationStatus
from skale.utils.contracts_provision.main import _skip_evm_time
from skale.utils.contracts_provision.utils import generate_random_name
from tests.constants import (
    D_DELEGATION_AMOUNT,
    D_DELEGATION_INFO,
    D_DELEGATION_PERIOD,
    D_VALIDATOR_ID,
    DELEGATION_STRUCT_LEN,
    MONTH_IN_SECONDS,
    NOT_EXISTING_ID,
)


def _delegate_and_activate(skale, validator_id=D_VALIDATOR_ID):
    skale.delegation_controller.delegate(
        validator_id=validator_id,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True,
    )
    delegations = skale.delegation_controller.get_all_delegations_by_validator(validator_id)
    skale.delegation_controller.accept_pending_delegation(delegations[-1]['id'], wait_for=True)
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS)


def _get_number_of_delegations(skale, validator_id=D_VALIDATOR_ID):
    return skale.delegation_controller._get_delegation_ids_len_by_validator(validator_id)


def test_get_raw_not_exist(skale):
    with pytest.raises((ContractLogicError, ValueError)):
        skale.delegation_controller._DelegationController__raw_get_delegation(NOT_EXISTING_ID)


def test_get_delegation(skale, validator):
    validator_id = validator
    delegations_by_validator = skale.delegation_controller._get_delegation_ids_by_validator(
        validator_id
    )
    delegation_id = delegations_by_validator[-1]
    delegation_struct = skale.delegation_controller._DelegationController__raw_get_delegation(
        delegation_id
    )
    assert delegation_struct[1] == validator_id
    assert len(delegation_struct) == DELEGATION_STRUCT_LEN

    delegation = skale.delegation_controller.get_delegation(delegation_id)
    assert list(delegation.keys()) == FIELDS
    assert delegation['validator_id'] == validator_id
    assert [k for k, v in delegation.items() if v is None] == []


def test_delegate(skale, validator):
    validator_id = validator
    num_of_delegations_before = _get_number_of_delegations(skale)
    delegated_now_before = skale.delegation_controller.get_delegated_to_validator_now(validator_id)
    delegated_amount_before = skale.delegation_controller.get_delegated_amount(skale.wallet.address)

    _delegate_and_activate(skale)
    num_of_delegations_after = _get_number_of_delegations(skale)
    assert num_of_delegations_after == num_of_delegations_before + 1

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=validator_id
    )
    assert delegations[-1]['info'] == D_DELEGATION_INFO

    delegated_now_after = skale.delegation_controller.get_delegated_to_validator_now(validator_id)
    delegated_amount_after = skale.delegation_controller.get_delegated_amount(skale.wallet.address)
    assert delegated_now_after == delegated_now_before + D_DELEGATION_AMOUNT
    assert delegated_amount_after == delegated_amount_before + D_DELEGATION_AMOUNT

    month = skale.time_helpers_with_debug.get_current_month()
    res = skale.delegation_controller.get_delegated_to_validator(validator_id, month)
    assert isinstance(res, int)


def test_get_delegation_ids_by_validator(skale, validator):
    validator_id = validator
    delegation_ids = skale.delegation_controller._get_delegation_ids_by_validator(
        validator_id=validator_id
    )
    delegation_ids_len = skale.delegation_controller._get_delegation_ids_len_by_validator(
        validator_id
    )
    assert len(delegation_ids) == delegation_ids_len
    latest_delegation = skale.delegation_controller.get_delegation(delegation_ids[-1])
    assert latest_delegation['validator_id'] == validator_id


def test_get_all_delegations_by_holder(skale):
    delegations = skale.delegation_controller.get_all_delegations_by_holder(skale.wallet.address)
    assert all([delegation['address'] == skale.wallet.address for delegation in delegations])


def test_get_all_delegations_by_validator(skale, validator):
    validator_id = validator
    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=validator_id
    )
    assert all([delegation['validator_id'] == validator_id for delegation in delegations])


def test_accept_pending_delegation(skale, validator):
    validator_id = validator
    info = f'{D_DELEGATION_INFO}-{generate_random_name()}'
    skale.delegation_controller.delegate(
        validator_id=validator_id,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=info,
        wait_for=True,
    )
    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=validator_id
    )
    delegation_id = delegations[-1]['id']
    assert delegations[-1]['status'] == DelegationStatus.PROPOSED
    assert delegations[-1]['info'] == info
    skale.delegation_controller.accept_pending_delegation(delegation_id)
    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=validator_id
    )
    assert delegations[-1]['id'] == delegation_id
    assert delegations[-1]['status'] == DelegationStatus.ACCEPTED
    assert delegations[-1]['info'] == info


def test_cancel_pending_delegation(skale, validator):
    validator_id = validator
    skale.delegation_controller.delegate(
        validator_id=validator_id,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True,
    )
    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=validator_id
    )
    delegation_id = delegations[-1]['id']
    assert delegations[-1]['status'] == DelegationStatus.PROPOSED
    skale.delegation_controller.cancel_pending_delegation(delegation_id, wait_for=True)
    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=validator_id
    )
    assert delegations[-1]['id'] == delegation_id
    assert delegations[-1]['status'] == DelegationStatus.CANCELED


def test_request_undelegate(skale, validator):
    validator_id = validator
    skale.delegation_controller.delegate(
        validator_id=validator_id,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True,
    )
    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=validator_id
    )
    delegation_id = delegations[-1]['id']
    skale.delegation_controller.accept_pending_delegation(delegations[-1]['id'], wait_for=True)

    # Transaction failed if delegation period is in progress
    with pytest.raises(DryRunRevertError):
        tx_res = skale.delegation_controller.request_undelegation(
            delegation_id, wait_for=True, raise_for_status=False
        )
        tx_res.raise_for_status()

    # Skip time longer than delegation period
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * (D_DELEGATION_PERIOD + 1))

    skale.delegation_controller.request_undelegation(
        delegation_id, wait_for=True, raise_for_status=False
    )

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=validator_id
    )
    assert delegations[-1]['id'] == delegation_id
    assert delegations[-1]['status'] == DelegationStatus.UNDELEGATION_REQUESTED
