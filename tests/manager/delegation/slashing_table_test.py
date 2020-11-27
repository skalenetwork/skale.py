def test_slashing_table_get_set(skale):
    penalty_value = 50
    offense = 'FailedDkg'
    skale.slashing_table.set_penalty(offense, penalty_value, wait_for=True)

    expected_penalty = penalty_value
    penalty = skale.slashing_table.get_penalty(offense)
    assert penalty == expected_penalty
