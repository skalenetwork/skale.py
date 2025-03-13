from tests.constants import DEFAULT_SCHAIN_ID, DEFAULT_SCHAIN_NAME


def test_get_previous_groups_public_key(skale):
    group_id = skale.web3.keccak(text=DEFAULT_SCHAIN_NAME)
    public_key = skale.key_storage.get_previous_public_key(group_id)
    assert isinstance(public_key, tuple)
    assert len(public_key) == 2
    assert isinstance(public_key[0], tuple) and len(public_key[0]) == 2
    assert isinstance(public_key[1], tuple) and len(public_key[1]) == 2


def test_get_all_previous_groups_public_keys(skale):
    # TODO: Improve test
    group_id = skale.web3.keccak(text=DEFAULT_SCHAIN_NAME)
    keys = skale.key_storage.get_all_previous_public_keys(group_id)
    assert keys == []


def test_get_group_public_key(skale):
    assert skale.key_storage.get_common_public_key(DEFAULT_SCHAIN_ID) == ((0, 0), (0, 0))
