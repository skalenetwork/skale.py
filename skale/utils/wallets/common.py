import struct
from abc import ABC, abstractmethod

DEFAULT_BIP32_PATH = "44'/60'/0'/0/0"


class BaseWallet(ABC):
    @abstractmethod
    def sign(tx):
        pass

    @property
    @abstractmethod
    def address(self):
        pass

    @property
    @abstractmethod
    def public_key(self):
        pass


def encode_bip32_path(path=DEFAULT_BIP32_PATH):
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


def derivation_path_prefix(bin32_path=DEFAULT_BIP32_PATH):
    encoded_path = encode_bip32_path(bin32_path)
    encoded_path_len_bytes = (len(encoded_path) // 4).to_bytes(1, 'big')
    return encoded_path_len_bytes + encoded_path


def chunks(sequence, size):
    return (sequence[pos:pos + size] for pos in range(0, len(sequence), size))
