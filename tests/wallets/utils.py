from eth_account.datastructures import SignedMessage, SignedTransaction
from hexbytes import HexBytes
from sgx.sgx import Account

from skale.utils.web3_utils import (
    private_key_to_address,
    private_key_to_public,
    to_checksum_address,
)
from tests.constants import ETH_PRIVATE_KEY

ADDRESS = to_checksum_address(private_key_to_address(ETH_PRIVATE_KEY))
PUBLIC_KEY = private_key_to_public(ETH_PRIVATE_KEY)


class SgxClient:
    def __init__(self, endpoint, path_to_cert=None):
        pass

    def generate_key(self):
        return Account(name='NEK:aaabbb', address=ADDRESS, public_key=PUBLIC_KEY)

    def get_account(self, key_name):
        return Account(name='NEK:aaabbb', address=ADDRESS, public_key=PUBLIC_KEY)

    def sign(self, transaction_dict, key_name):
        return SignedTransaction(
            raw_transaction=HexBytes('0x000000000000'),
            hash=HexBytes('0x000000000000'),
            r=100000000000,
            s=100000000000,
            v=37,
        )

    def sign_hash(self, message, key_name, chain_id):
        return SignedMessage(
            message_hash=HexBytes('0x31323331'),
            r=123,
            s=123,
            v=27,
            signature=HexBytes('0x6161616161613131313131'),
        )


class BadSgxClient:
    def __init__(self, endpoint, path_to_cert=None):
        pass

    def generate_key(self):
        return Account(name='NEK:aaabbb', address=ADDRESS, public_key=PUBLIC_KEY)

    def get_account(self, key_name):
        return Account(name='NEK:aaabbb', address=ADDRESS, public_key=PUBLIC_KEY)

    def sign(self, transaction_dict, key_name):
        raise ValueError('Test Error')

    def sign_hash(self, message, key_name, chain_id):
        raise ValueError('Test error')
