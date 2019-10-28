import logging
import os
import struct

from hexbytes import HexBytes
from eth_account.datastructures import AttributeDict
from eth_account.internal.transactions import encode_transaction
from eth_account.internal.transactions import \
    serializable_unsigned_transaction_from_dict as tx_from_dict
from eth_utils.crypto import keccak
from ledgerblue.comm import getDongle
from rlp import encode

from skale.utils.helper import await_receipt
from skale.utils.helper import get_nonce

logger = logging.getLogger(__name__)

DEFAULT_BIP32_PATH = "44'/60'/0'/0/0"
CHUNK_SIZE = 255
CLA = b'\xe0'
INS = b'\x04'
P1_FIRST = b'\x00'
P1_SUBSEQUENT = b'\x80'
P2 = b'\x00'


def encode_bip32_path(path):
    if len(path) == 0:
        return b''
    encoded_chunks = []
    for bip32_chunk in path.split('/'):
        chunk = bip32_chunk.split('\'')
        if len(chunk) == 1:
            encoded_chunk = struct.pack('>I', int(chunk[0]))
        else:
            encoded_chunk = struct.pack('>I', 0x80000000 | int(chunk[0]))
        encoded_chunks.append(encoded_chunk)

    return b''.join(encoded_chunks)


def chunks(sequence, size):
    return (sequence[pos:pos + size] for pos in range(0, len(sequence), size))


def make_payload(tx, bip32_path=DEFAULT_BIP32_PATH):
    encoded_tx = encode(tx)
    encoded_path = encode_bip32_path(bip32_path)
    encoded_path_len_bytes = (len(encoded_path) // 4).to_bytes(1, 'big')
    return encoded_path_len_bytes + encoded_path + encoded_tx


def exchange_by_chunks(dongle, payload):
    p1 = P1_FIRST
    for chunk in chunks(payload, CHUNK_SIZE):
        chunk_size_bytes = len(chunk).to_bytes(1, 'big')
        apdu = b''.join([CLA, INS, p1, P2, chunk_size_bytes, chunk])
        exchange_result = dongle.exchange(apdu)
        p1 = P1_SUBSEQUENT
    return exchange_result


def parse_result(tx, exchange_result):
    _v = exchange_result[0]
    _r = int((exchange_result[1:1 + 32]).hex(), 16)
    _s = int((exchange_result[1 + 32: 1 + 32 + 32]).hex(), 16)

    enctx = encode_transaction(tx, (_v, _r, _s))
    transaction_hash = keccak(enctx)

    signed_txn = AttributeDict({
        'rawTransaction': HexBytes(enctx),
        'hash': HexBytes(transaction_hash),
        'r': _r,
        's': _s,
        'v': _v,
    })
    return signed_txn


def sign_with_hw(tx_dict, bip32_path=DEFAULT_BIP32_PATH):
    tx = tx_from_dict(tx_dict)
    payload = make_payload(tx, bip32_path)
    dongle = getDongle(True)
    exchange_result = exchange_by_chunks(dongle, payload)
    return parse_result(tx, exchange_result)


def hw_transaction(skale, wallet):
    txn = {
        'to': os.environ['ADDRESS'],
        'value': 1,
        'gas': 200000,
        'gasPrice': 1,
        'nonce': get_nonce(skale, wallet['address']),
        'chainId': None,
    }
    signed_txn = sign_with_hw(txn)
    tx = skale.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    reciept = await_receipt(skale.web3, tx)
    return reciept


def hardware_sign_and_send(skale, method, gas_amount, wallet):
    address_from = wallet['address']
    # address_to = Web3.toChecksumAddress('1057dc7277a319927D3eB43e05680B75a00eb5f4')
    # print('BALANCE FROM BEFORE {}'.format(skale.web3.eth.getBalance(address_from)))
    # print('BALANCE TO BEFORE {}'.format(skale.web3.eth.getBalance(address_to)))
    eth_nonce = get_nonce(skale, address_from)
    tx_dict = method.buildTransaction({
        'gas': gas_amount,
        'nonce': eth_nonce  # + 2
    })
    signed_txn = sign_with_hw(tx_dict)
    tx = skale.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    logger.info(
        f'{method.__class__.__name__} - transaction_hash: {skale.web3.toHex(tx)}'
    )
    return tx
