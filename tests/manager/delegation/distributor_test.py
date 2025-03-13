"""Tests for contracts/delegation/distributor.py"""

from tests.constants import D_VALIDATOR_ID


def test_get_earned_bounty_amount(skale):
    res = skale.distributor.get_earned_bounty_amount(D_VALIDATOR_ID, skale.wallet.address)
    assert res['earned'] == 0


def test_get_earned_fee_amount(skale):
    res = skale.distributor.get_earned_fee_amount(skale.wallet.address)
    assert res['earned'] == 0


# todo: improve test
def test_withdraw_bounty(skale):
    tx_res = skale.distributor.withdraw_bounty(
        validator_id=D_VALIDATOR_ID, to=skale.wallet.address, wait_for=True
    )
    assert tx_res.receipt['status'] == 1


# todo: improve test
def test_withdraw_fee(skale):
    tx_res = skale.distributor.withdraw_fee(to=skale.wallet.address, wait_for=True)
    assert tx_res.receipt['status'] == 1
