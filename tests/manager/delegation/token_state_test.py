def test_get_and_update_locked_amount(skale):
    res = skale.token_state.get_and_update_locked_amount(skale.wallet.address)
    assert res > 0
