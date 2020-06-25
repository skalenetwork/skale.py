import mock
import web3
from mock import Mock
from hexbytes import HexBytes

from skale.contracts.dkg import G2Point, KeyShare

from tests.constants import (DEFAULT_NODE_NAME, DEFAULT_SCHAIN_ID,
                             EMPTY_SCHAIN_ARR, DEFAULT_SCHAIN_NAME,
                             MIN_NODES_IN_SCHAIN, DEFAULT_SCHAIN_INDEX)

def test_get_broadcasted_data(skale):
    broadcasted_data = skale.key_storage.get_broadcasted_data(DEFAULT_SCHAIN_ID, 0)
    assert broadcasted_data[0] == [["", ""], ""]
    assert broadcasted_data[1] == [0, 0, 0, 0]


def test_get_bls_public_key(skale):
    group_id = skale.web3.sha3(text=DEFAULT_SCHAIN_NAME)
    assert skale.key_storage.get_bls_public_key(group_id, 0) == [0, 0, 0, 0]
