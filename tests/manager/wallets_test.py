from tests.manager.delegation.validator_service_test import _generate_new_validator


def test_get_validator_balance(skale):
    _generate_new_validator(skale)
    latest_id = skale.validator_service.number_of_validators()
    assert skale.wallets.get_validator_balance(latest_id) == 0
