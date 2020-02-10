""" Tests for contracts/delegation/delegation_controller.py """

import pytest
from tests.constants import NOT_EXISTING_ID, D_DELEGATION_ID

from skale.contracts.delegation.delegation_controller import FIELDS


def test_get_raw_not_exist(skale):
    with pytest.raises(ValueError):
        skale.delegation_controller._DelegationController__raw_get_delegation(NOT_EXISTING_ID)


def test_get(skale):
    delegation = skale.delegation_controller.get_delegation(D_DELEGATION_ID)
    assert list(delegation.keys()) == FIELDS
    assert [k for k, v in delegation.items() if v is None] == []
