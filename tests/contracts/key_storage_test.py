from tests.constants import (DEFAULT_SCHAIN_ID, DEFAULT_SCHAIN_NAME)


def test_get_broadcasted_data(skale):
    group_index = b'e629fa6598d732768f7c726b4b621285'
    broadcasted_data = skale.key_storage.get_broadcasted_data(group_index, 0).call()
    assert broadcasted_data[0] == [["", ""], ""]
    assert broadcasted_data[1] == [0, 0, 0, 0]


def test_get_bls_public_key(skale):
    group_index = b'e629fa6598d732768f7c726b4b621285'
    assert skale.key_storage.get_bls_public_key(group_index, 0).call() == [0, 0, 0, 0]


def test_get_previous_groups_public_key(skale):
    group_index = b'e629fa6598d732768f7c726b4b621285'
    public_key = skale.key_storage.get_previous_public_key(group_index).call()
    assert len(public_key) == 4


def test_get_group_public_key(skale):
    group_index = b'e629fa6598d732768f7c726b4b621285'
    assert skale.key_storage.get_groups_public_key(group_index).call() == [0, 0, 0, 0]
