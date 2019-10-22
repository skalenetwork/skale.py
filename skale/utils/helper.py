#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" SKALE helper utilities """

import ipaddress
import json
import logging
import random
import socket
import string
import sys
from logging import Formatter, StreamHandler
from random import randint
from time import sleep

from eth_keys import keys
from web3 import Web3

logger = logging.getLogger(__name__)


def format(fields):
    """
        Transform array to object with passed fields
        Usage:
        @format(['field_name1', 'field_name2'])
        def my_method()
            return [0, 'Test']

        => {'field_name1': 0, 'field_name2': 'Test'}
    """

    def real_decorator(function):
        def wrapper(*args, **kwargs):
            result = function(*args, **kwargs)

            if result is None:
                return None

            obj = {}
            for i, field in enumerate(fields):
                obj[field] = result[i]
            return obj

        return wrapper

    return real_decorator


def get_receipt(web3, tx):
    return web3.eth.getTransactionReceipt(tx)


def get_eth_nonce(web3, address):
    return web3.eth.getTransactionCount(address)


def get_nonce(skale, address):
    lib_nonce = skale.nonces.get(address)
    if not lib_nonce:
        lib_nonce = get_eth_nonce(skale.web3, address)
        skale.nonces.get(address)
    else:
        lib_nonce += lib_nonce
    return lib_nonce


def sign_and_send(skale, method, gas_amount, wallet):
    eth_nonce = get_nonce(skale, wallet['address'])
    logger.info(f'Method {method}. Transaction nonce: {eth_nonce}')
    txn = method.buildTransaction({
        'gas': gas_amount,
        'nonce': eth_nonce  # + 2
    })
    signed_txn = skale.web3.eth.account.signTransaction(
        txn, private_key=wallet['private_key'])
    tx = skale.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    logger.info(
        f'{method.__class__.__name__} - transaction_hash: {skale.web3.toHex(tx)}'
    )
    return tx


def await_receipt(web3, tx, retries=10, timeout=5):
    for _ in range(0, retries):
        receipt = get_receipt(web3, tx)
        if receipt is not None:
            return receipt
        sleep(timeout)  # pragma: no cover
    return None  # pragma: no cover


def ip_from_bytes(bytes):
    return socket.inet_ntoa(bytes)


def ip_to_bytes(ip):  # pragma: no cover
    return socket.inet_aton(ip)


def is_valid_ipv4_address(address):
    try:
        ipaddress.IPv4Address(address)
    except ValueError:
        return False
    return True


def get_abi(abi_filepath=None):
    with open(abi_filepath) as data_file:
        return json.load(data_file)


def generate_nonce():  # pragma: no cover
    return randint(0, 65534)


def random_string(size=6, chars=string.ascii_lowercase):  # pragma: no cover
    return ''.join(random.choice(chars) for x in range(size))


def generate_random_ip():  # pragma: no cover
    return '.'.join('%s' % random.randint(0, 255) for i in range(4))


def generate_random_name(len=8):  # pragma: no cover
    return ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=len))


def generate_random_port():  # pragma: no cover
    return random.randint(0, 60000)


def generate_custom_config(ip, ws_port):
    if not ip or not ws_port:
        raise ValueError(
            f'For custom init you should provide ip and ws_port: {ip}, {ws_port}'
        )
    return {
        'ip': ip,
        'ws_port': ws_port,
    }


def send_eth(web3, account, amount, wallet):
    eth_nonce = get_eth_nonce(web3, wallet['address'])
    logger.info(f'Transaction nonce {eth_nonce}')
    txn = {
        'to': account,
        'from': wallet['address'],
        'value': amount,
        'gasPrice': web3.eth.gasPrice,
        'gas': 22000,
        'nonce': eth_nonce
    }
    signed_txn = web3.eth.account.signTransaction(
        txn, private_key=wallet['private_key'])
    tx = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

    logger.info(
        f'ETH transfer {wallet["address"]} => {account}, {amount} wei, tx: {web3.toHex(tx)}'
    )
    return tx


def private_key_to_public(pr):
    pr_bytes = Web3.toBytes(hexstr=pr)
    pk = keys.PrivateKey(pr_bytes)
    return pk.public_key


def public_key_to_address(pk):
    hash = Web3.sha3(hexstr=str(pk))
    return Web3.toHex(hash[-20:])


def private_key_to_address(pr):
    pk = private_key_to_public(pr)
    return public_key_to_address(pk)


def check_receipt(receipt):
    if receipt['status'] != 1:  # pragma: no cover
        raise ValueError("Transaction failed, see receipt", receipt)
    return True


def init_default_logger():  # pragma: no cover
    handlers = []
    formatter = Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stream_handler = StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    handlers.append(stream_handler)

    logging.basicConfig(level=logging.DEBUG, handlers=handlers)
