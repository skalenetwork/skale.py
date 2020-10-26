from eth_account.datastructures import AttributeDict
from hexbytes import HexBytes
from skale.utils.web3_utils import (
    private_key_to_address,
    private_key_to_public,
    to_checksum_address
)
from tests.constants import ETH_PRIVATE_KEY


class SgxClientMock:
    ADDRESS = to_checksum_address(
        private_key_to_address(ETH_PRIVATE_KEY)
    )
    PUBLIC_KEY = private_key_to_public(ETH_PRIVATE_KEY)

    def __init__(self, endpoint, path_to_cert=None):
        pass

    def generate_key(self):
        return AttributeDict(
            name='NEK:aaabbb',
            address=SgxClientMock.ADDRESS,
            public_key=SgxClientMock.PUBLIC_KEY
        )

    def get_account(self, key_name):
        return AttributeDict({
            'address': SgxClientMock.ADDRESS,
            'public_key': SgxClientMock.PUBLIC_KEY
        })

    def sign(self, transaction_dict, key_name):
        return AttributeDict({
            'rawTransaction': HexBytes('0x000000000000'),
            'hash': HexBytes('0x000000000000'),
            'r': 100000000000,
            's': 100000000000,
            'v': 37,
        })

    def sign_hash(self, message, key_name, chain_id):
        return AttributeDict({
            'messageHash': HexBytes('0x31323331'),
            'r': 123,
            's': 123,
            'v': 27,
            'signature': HexBytes('0x6161616161613131313131')
        })


class RedisClientMock:
    response_message: dict = {}

    class SubMock:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def get_message(self) -> dict:
            return RedisClientMock.response_message

        def subscribe(self, channel: str):
            pass

    def __init__(self, *args, **kwargs) -> None:
        pass

    @classmethod
    def from_url(cls, url: str, db: int):
        return RedisClientMock()

    def publish(self, channel: str, message: dict) -> None:
        pass

    def pubsub(self) -> SubMock:
        return RedisClientMock.SubMock()
