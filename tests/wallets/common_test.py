from unittest import mock

import pytest
import web3

from skale.transactions.exceptions import ChainIdError
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet
from skale.wallets.common import ensure_chain_id
from tests.constants import ENDPOINT, ETH_PRIVATE_KEY


def get_tx_dict():
    return {
        'to': '0x0000000000000000000000000000000000000000',
        'value': 0,
        'gasPrice': 1,
        'gas': 22000,
        'nonce': 0,
    }


def test_ensure_chain_id(skale):
    tx_dict = get_tx_dict()
    ensure_chain_id(tx_dict, skale.web3)
    assert isinstance(tx_dict['chainId'], int)
    assert tx_dict['chainId'] == skale.web3.eth.chain_id


def test_ensure_chain_id_fail(skale):
    tx_dict = get_tx_dict()
    with mock.patch.object(web3.eth.Eth, 'chain_id', new=None):
        with pytest.raises(ChainIdError):
            ensure_chain_id(tx_dict, skale.web3)


def test_ensure_chain_id_web3_wallet():
    tx_dict = get_tx_dict()
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    wallet.sign(tx_dict)
