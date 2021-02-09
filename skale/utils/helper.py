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

logger = logging.getLogger(__name__)


def decapitalize(s):
    return s[:1].lower() + s[1:] if s else ''


def format_fields(fields, flist=False):
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

            if flist:
                formatted_list = []
                for item in result:
                    obj = {}
                    for i, field in enumerate(fields):
                        obj[field] = item[i]
                    formatted_list.append(obj)
                return formatted_list

            obj = {}
            for i, field in enumerate(fields):
                obj[field] = result[i]
            return obj

        return wrapper

    return real_decorator


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


def add_0x_prefix(bytes_string):  # pragma: no cover
    return '0x' + bytes_string


def rm_0x_prefix(bytes_string):
    if bytes_string.startswith('0x'):
        return bytes_string[2:]
    return bytes_string


def init_default_logger():  # pragma: no cover
    handlers = []
    formatter = Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stream_handler = StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    handlers.append(stream_handler)

    logging.basicConfig(level=logging.DEBUG, handlers=handlers)


def chunk(in_string, num_chunks):  # pragma: no cover
    chunk_size = len(in_string) // num_chunks
    if len(in_string) % num_chunks:
        chunk_size += 1
    iterator = iter(in_string)
    for _ in range(num_chunks):
        accumulator = []
        for _ in range(chunk_size):
            try:
                accumulator.append(next(iterator))
            except StopIteration:
                break
        yield ''.join(accumulator)


def split_public_key(public_key: str) -> list:
    public_key = rm_0x_prefix(public_key)
    pk_parts = list(chunk(public_key, 2))
    return list(map(bytes.fromhex, pk_parts))


def get_contracts_info(contracts_data):
    contracts_info = {}
    for contract_info in contracts_data:
        contracts_info[contract_info.name] = contract_info
    return contracts_info


def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
