""" SKALE contract manager test """

from tests.constants import TEST_CONTRACT_NAME, ZERO_ADDRESS, TEST_CONTRACT_NAME_HASH


def test_get_contract_address(skale):
    contract_address = skale.get_contract_address(TEST_CONTRACT_NAME)
    assert ZERO_ADDRESS != contract_address


def test_get_contract_hash_by_name(skale):
    contract_name_hash = skale.contract_manager.get_contract_hash_by_name(
        TEST_CONTRACT_NAME)
    assert TEST_CONTRACT_NAME_HASH == contract_name_hash
