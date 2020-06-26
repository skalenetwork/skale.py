from tests.constants import (DEFAULT_SCHAIN_ID, DEFAULT_SCHAIN_NAME)


def test_get_broadcasted_data(skale):
    broadcasted_data = skale.key_storage.get_broadcasted_data(DEFAULT_SCHAIN_ID, 0).call()
    assert broadcasted_data[0] == [["", ""], ""]
    assert broadcasted_data[1] == [0, 0, 0, 0]


def test_get_bls_public_key(skale):
    group_id = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    assert skale.key_storage.get_bls_public_key(group_id, 0).call() == [0, 0, 0, 0]


def test_get_previous_groups_public_key(skale):
    group_id = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    public_key = skale.key_storage.get_previous_groups_public_key(group_id).call()
    assert len(public_key) == 4


def test_get_group_public_key(skale):
    assert skale.key_storage.get_groups_public_key(DEFAULT_SCHAIN_ID).call() == [0, 0, 0, 0]
