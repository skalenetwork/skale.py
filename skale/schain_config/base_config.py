#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019-Present SKALE Labs
#
#   SKALE.py is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   SKALE.py is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with SKALE.py.  If not, see <https://www.gnu.org/licenses/>.

from web3 import Web3
from Crypto.Hash import keccak

from skale.schain_config import NODE_OWNER_ALLOC, SCHAIN_OWNER_ALLOC, PRECOMPILED_IMA_CONTRACTS


def add_to_accounts(accounts, account, balance, code=None, storage={}, nonce=0):
    assert isinstance(code, str) or code is None
    assert isinstance(storage, dict) or storage is None
    acc_fx = Web3.toChecksumAddress(account)
    if str(acc_fx) not in accounts:
        accounts[acc_fx] = {"balance": str(balance)}
        if code:
            accounts[acc_fx]['code'] = code
            accounts[acc_fx]['storage'] = storage
            accounts[acc_fx]['nonce'] = str(nonce)


def update_accounts(schain, schain_nodes, ima_data=None):
    accounts = {}
    add_to_accounts(accounts, schain['owner'], SCHAIN_OWNER_ALLOC)
    for node in schain_nodes:
        if str(node['owner']) not in accounts:
            add_to_accounts(accounts, node['owner'], NODE_OWNER_ALLOC)
    add_to_accounts(
        accounts,
        '0xD2001000000000000000000000000000000000D2',
        0,
        *_generate_context_predeployed_smart_contract(
            schain['owner'],
            schain['name']
        )
    )
    if ima_data:
        add_ima_accounts(accounts, ima_data)
    return accounts


def update_base_config(base_config, schain, schain_nodes, ima_data=None):
    new_accounts = update_accounts(schain, schain_nodes, ima_data=ima_data)
    base_config['accounts'] = {**base_config['accounts'], **new_accounts}
    add_chain_id(base_config, schain['name'])


def add_ima_accounts(accounts, ima_data):
    for contract_name in PRECOMPILED_IMA_CONTRACTS:
        add_to_accounts(
            accounts=accounts,
            account=ima_data[f'{contract_name}_address'],
            balance=0,
            code=ima_data[f'{contract_name}_bytecode'],
        )


def _generate_context_predeployed_smart_contract(owner_address: str,
                                                 schain_name: str) -> (str, dict):
    code = ('0x608060405234801561001057600080fd5b506004361061005e576000357c0100' +
            '0000000000000000000000000000000000000000000000000000009004806315' +
            'cd7a2d1461006357806367091a01146100e657806383e781fe1461012a575b60' +
            '0080fd5b61006b610174565b6040518080602001828103825283818151815260' +
            '200191508051906020019080838360005b838110156100ab5780820151818401' +
            '52602081019050610090565b50505050905090810190601f1680156100d85780' +
            '820380516001836020036101000a031916815260200191505b50925050506040' +
            '5180910390f35b610128600480360360208110156100fc57600080fd5b810190' +
            '80803573ffffffffffffffffffffffffffffffffffffffff1690602001909291' +
            '90505050610216565b005b6101326102b2565b604051808273ffffffffffffff' +
            'ffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffff' +
            'ffffff16815260200191505060405180910390f35b6060600180546001816001' +
            '16156101000203166002900480601f0160208091040260200160405190810160' +
            '4052809291908181526020018280546001816001161561010002031660029004' +
            '801561020c5780601f106101e15761010080835404028352916020019161020c' +
            '565b820191906000526020600020905b81548152906001019060200180831161' +
            '01ef57829003601f168201915b5050505050905090565b600080905490610100' +
            '0a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffff' +
            'ffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffff' +
            'ffffffffff161461026f57600080fd5b806000806101000a81548173ffffffff' +
            'ffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffff' +
            'ffffffffffffffffffff16021790555050565b60008060009054906101000a90' +
            '0473ffffffffffffffffffffffffffffffffffffffff1690509056fea165627a' +
            '7a723058203d58598dee9113d96d02a8821205cf2af6e04d52d4d3b52f4563f7' +
            '7936acb5490029')
    storage = {hex(0): str(Web3.toChecksumAddress(owner_address))}
    storage = {**storage, **_string_to_storage(1, schain_name)}

    return code, storage


def _string_to_storage(slot: int, string: str) -> dict:
    # https://solidity.readthedocs.io/en/develop/miscellaneous.html#bytes-and-string
    storage = dict()
    binary = string.encode()
    length = len(binary)
    if length < 32:
        binary += (2 * length).to_bytes(32 - length, 'big')
        storage[hex(slot)] = '0x' + binary.hex()
    else:
        storage[hex(slot)] = hex(2 * length + 1)

        keccak_hash = keccak.new(digest_bits=256)
        keccak_hash.update(slot.to_bytes(32, 'big'))
        offset = int.from_bytes(keccak_hash.digest(), 'big')

        def chunks(size, source):
            for i in range(0, len(source), size):
                yield source[i:i + size]

        for index, data in enumerate(chunks(32, binary)):
            if len(data) < 32:
                data += int(0).to_bytes(32 - len(data), 'big')
            storage[hex(offset + index)] = '0x' + data.hex()
    return storage


def add_chain_id(base_config, schain_name):
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(schain_name.encode("utf-8"))
    hash_ = keccak_hash.hexdigest()
    hash_ = hash_[:13]			# use 52 bits
    base_config['params']['chainID'] = "0x" + hash_
