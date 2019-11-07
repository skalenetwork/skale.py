import logging

from hexbytes import HexBytes
from eth_account.datastructures import AttributeDict
from eth_account._utils.transactions import encode_transaction
from eth_account._utils.transactions import \
    serializable_unsigned_transaction_from_dict as tx_from_dict
from eth_utils.crypto import keccak
from ledgerblue.comm import getDongle
from rlp import encode
from skale.utils.web3_utils import get_eth_nonce, public_key_to_address, \
                                   to_checksum_address

from skale.utils.wallets.common import chunks, BaseWallet, derivation_path_prefix

logger = logging.getLogger(__name__)


class LedgerWallet(BaseWallet):
    CHUNK_SIZE = 255
    CLA = b'\xe0'

    def __init__(self, debug=False):
        self.dongle = getDongle(debug)
        self._address, self._public_key = self.get_address_with_public_key()

    @property
    def address(self):
        return self._address

    @property
    def public_key(self):
        return self._public_key

    # todo: remove this method after making software wallet as class
    def __getitem__(self, key):
        items = {'address': self.address, 'public_key': self.public_key}
        return items[key]

    @classmethod
    def make_payload(cls, data=''):
        encoded_data = encode(data)
        path_prefix = derivation_path_prefix()
        return path_prefix + encoded_data

    @classmethod
    def parse_sign_result(cls, tx, exchange_result):
        sign_v = exchange_result[0]
        sign_r = int((exchange_result[1:1 + 32]).hex(), 16)
        sign_s = int((exchange_result[1 + 32: 1 + 32 + 32]).hex(), 16)

        enctx = encode_transaction(tx, (sign_v, sign_r, sign_s))
        transaction_hash = keccak(enctx)

        signed_txn = AttributeDict({
            'rawTransaction': HexBytes(enctx),
            'hash': HexBytes(transaction_hash),
            'v': sign_v,
            'r': sign_r,
            's': sign_s,
        })
        return signed_txn

    def exchange_sign_payload_by_chunks(self, payload):
        INS = b'\x04'
        P1_FIRST = b'\x00'
        P1_SUBSEQUENT = b'\x80'
        P2 = b'\x00'

        p1 = P1_FIRST
        for chunk in chunks(payload, LedgerWallet.CHUNK_SIZE):
            chunk_size_bytes = len(chunk).to_bytes(1, 'big')
            apdu = b''.join([
                LedgerWallet.CLA, INS, p1, P2, chunk_size_bytes, chunk
            ])
            exchange_result = self.dongle.exchange(apdu)
            p1 = P1_SUBSEQUENT
        return exchange_result

    def sign(self, tx_dict):
        tx = tx_from_dict(tx_dict)
        payload = LedgerWallet.make_payload(tx)
        exchange_result = self.exchange_sign_payload_by_chunks(payload)
        return LedgerWallet.parse_sign_result(tx, exchange_result)

    @classmethod
    def parse_derive_result(cls, exchange_result):
        pk_len = exchange_result[0]
        pk = exchange_result[1: pk_len + 1].hex()[2:]
        address = public_key_to_address(pk)
        checksum_address = to_checksum_address(address)
        return checksum_address, pk

    def exchange_derive_payload(self, payload):
        INS = b'\x02'
        P1 = b'\x00'
        P2 = b'\x00'
        payload_size_in_bytes = len(payload).to_bytes(1, 'big')
        apdu = b''.join([
            LedgerWallet.CLA, INS, P1, P2,
            payload_size_in_bytes, payload
        ])
        return self.dongle.exchange(apdu)

    def get_address_with_public_key(self):
        payload = LedgerWallet.make_payload()
        exchange_result = self.exchange_derive_payload(payload)
        return LedgerWallet.parse_derive_result(exchange_result)


def hardware_sign_and_send(skale, method, gas_amount, wallet):
    address_from = wallet['address']
    eth_nonce = get_eth_nonce(skale.web3, address_from)
    tx_dict = method.buildTransaction({
        'gas': gas_amount,
        'nonce': eth_nonce
    })
    signed_txn = wallet.sign(tx_dict)
    tx = skale.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    logger.info(
        f'{method.__class__.__name__} - transaction_hash: {skale.web3.toHex(tx)}'
    )
    return tx