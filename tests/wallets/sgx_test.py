import mock

from hexbytes import HexBytes
from eth_account.datastructures import AttributeDict
from skale.wallets.sgx_wallet import SgxWallet


class SgxClient:
    def __init__(self, endpoint):
        pass

    def generate_key(self):
        return AttributeDict({
            'keyName': 'tmp_NEK:aaabbb',
            'address': '0xAB00000000000000000000000000000000000000',
            'publicKey': 'ab00000000000000000000000000000000000000',
        })

    def get_account(self, key_name):
        return AttributeDict({
            'address': '0xAB00000000000000000000000000000000000000',
            'publicKey': 'ab00000000000000000000000000000000000000',
        })

    def sign(self, transaction_dict, key_name):
        return AttributeDict({
            'rawTransaction': HexBytes('0x000000000000'),
            'hash': HexBytes('0x000000000000'),
            'r': 100000000000,
            's': 100000000000,
            'v': 37,
        })

    def rename_key(self, temp_key_name, new_key_name):
        pass


def test_sgx_sign():
    with mock.patch('skale.wallets.sgx_wallet.SgxClient',
                    new=SgxClient):
        wallet = SgxWallet('TEST_ENDPOINT')
        tx_dict = {
            'to': '0x1057dc7277a319927D3eB43e05680B75a00eb5f4',
            'value': 9,
            'gas': 200000,
            'gasPrice': 1,
            'nonce': 7,
            'chainId': None,
            'data': b'\x9b\xd9\xbb\xc6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x95qY\xc4i\xfc;\xba\xa8\xe3\x9e\xe0\xa3$\xc28\x8a\xd6Q\xe5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\xe0\xb6\xb3\xa7d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa8\xc0\x04/Rglamorous-kitalpha\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa
        }
        wallet.sign(tx_dict)
