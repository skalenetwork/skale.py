""" Tests for contracts/delegation/validator_service.py """

from skale.contracts.delegation.validator_service import FIELDS

from tests.constants import NOT_EXISTING_ID, D_VALIDATOR_ID


def test_get_raw_not_exist(skale):
    empty_struct = skale.validator_service._ValidatorService__get_raw(NOT_EXISTING_ID)
    assert empty_struct[0] == ''
    assert empty_struct[1] == '0x0000000000000000000000000000000000000000'


def test_get(skale):
    delegation = skale.validator_service.get(D_VALIDATOR_ID)
    assert list(delegation.keys()) == FIELDS
    assert [k for k, v in delegation.items() if v is None] == []
