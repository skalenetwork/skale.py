"""SKALE contract manager test"""

from skale_contracts.projects.skale_manager import SkaleManagerContract
from web3 import Web3

from skale.utils.constants import ZERO_ADDRESS
from tests.constants import TEST_CONTRACT_NAME, TEST_CONTRACT_NAME_HASH


def test_get_contract_address(skale):
    contract_address = skale.instance.get_contract_address(SkaleManagerContract.NODES)
    assert Web3.to_checksum_address(contract_address) != ZERO_ADDRESS


def test_get_contract_hash_by_name(skale):
    contract_name_hash = skale.contract_manager.get_contract_hash_by_name(TEST_CONTRACT_NAME)
    assert contract_name_hash == TEST_CONTRACT_NAME_HASH
