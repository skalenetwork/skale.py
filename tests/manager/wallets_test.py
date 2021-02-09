from skale.utils.account_tools import send_ether
from tests.manager.delegation.validator_service_test import _generate_new_validator


TEST_RECHARGE_VALUE = 1000


def test_get_validator_balance(skale):
    _generate_new_validator(skale)
    latest_id = skale.validator_service.number_of_validators()
    assert skale.wallets.get_validator_balance(latest_id) == 0


def test_recharge_validator_wallet(skale):
    _generate_new_validator(skale)
    latest_id = skale.validator_service.number_of_validators()
    assert skale.wallets.get_validator_balance(latest_id) == 0

    skale.wallets.recharge_validator_wallet(latest_id, value=TEST_RECHARGE_VALUE)
    srw_balance_after = skale.wallets.get_validator_balance(latest_id)
    assert srw_balance_after != 0
    assert srw_balance_after == TEST_RECHARGE_VALUE


def test_withdraw_funds_from_validator_wallet(skale):
    main_wallet = skale.wallet
    new_wallet = _generate_new_validator(skale)
    send_ether(skale.web3, main_wallet, new_wallet.address, 0.1)

    latest_id = skale.validator_service.number_of_validators()
    skale.wallets.recharge_validator_wallet(latest_id, value=TEST_RECHARGE_VALUE)
    assert skale.wallets.get_validator_balance(latest_id) == TEST_RECHARGE_VALUE

    skale.wallet = new_wallet
    skale.wallets.withdraw_funds_from_validator_wallet(amount=TEST_RECHARGE_VALUE)
    assert skale.wallets.get_validator_balance(latest_id) == 0
    skale.wallet = main_wallet
