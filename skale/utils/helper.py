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
"""SKALE helper utilities"""

import ipaddress
import json
import logging
import random
import socket
import string
import sys
from logging import Formatter, StreamHandler
from random import randint
from typing import Any, Callable, Dict, Generator, List, cast

from skale.config import ENV
from skale.types.node import Port
from eth_typing import ChecksumAddress


logger = logging.getLogger(__name__)


def decapitalize(s: str) -> str:
    return s[:1].lower() + s[1:] if s else ''


WrapperReturnType = Dict[str, Any] | List[Dict[str, Any]] | None


def format_fields(
    fields: list[str], flist: bool = False
) -> Callable[[Callable[..., List[Any]]], Callable[..., WrapperReturnType]]:
    """
    Transform array to object with passed fields
    Usage:
    @format(['field_name1', 'field_name2'])
    def my_method()
        return [0, 'Test']

    => {'field_name1': 0, 'field_name2': 'Test'}
    """

    def real_decorator(function: Callable[..., List[Any]]) -> Callable[..., WrapperReturnType]:
        def wrapper(*args: Any, **kwargs: Any) -> WrapperReturnType:
            result = function(*args, **kwargs)

            if result is None:
                return None

            if not isinstance(result, list) and not isinstance(result, tuple):
                return result

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


def ip_from_bytes(packed: bytes) -> str:
    return socket.inet_ntoa(packed)


def ip_to_bytes(ip: str) -> bytes:  # pragma: no cover
    return socket.inet_aton(ip)


def is_valid_ipv4_address(address: ChecksumAddress) -> bool:
    try:
        ipaddress.IPv4Address(address)
    except ValueError:
        return False
    return True


def get_abi(abi_filepath: str | None = None) -> dict[str, Any]:
    if abi_filepath:
        with open(abi_filepath, encoding='utf-8') as data_file:
            return cast(dict[str, Any], json.load(data_file))
    return {}


def get_skale_manager_address(abi_filepath: str | None = None) -> str:
    return cast(str, get_abi(abi_filepath)['skale_manager_address'])


def get_skale_ima_address(abi_filepath: str | None = None) -> str:
    return cast(str, get_abi(abi_filepath)['message_proxy_mainnet_address'])


def get_allocator_address(abi_filepath: str | None = None) -> str:
    return cast(str, get_abi(abi_filepath)['allocator_address'])


def generate_nonce() -> int:  # pragma: no cover
    return randint(0, 65534)


def random_string(size: int = 6, chars: str = string.ascii_lowercase) -> str:  # pragma: no cover
    return ''.join(random.choice(chars) for x in range(size))


def generate_random_ip() -> str:  # pragma: no cover
    return '.'.join('%s' % random.randint(0, 255) for i in range(4))


def generate_random_name(length: int = 8) -> str:  # pragma: no cover
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_random_port() -> Port:  # pragma: no cover
    return Port(random.randint(0, 60000))


def generate_custom_config(ip: str, ws_port: Port) -> dict[str, str | Port]:
    if not ip or not ws_port:
        raise ValueError(f'For custom init you should provide ip and ws_port: {ip}, {ws_port}')
    return {
        'ip': ip,
        'ws_port': ws_port,
    }


def add_0x_prefix(bytes_string: str) -> str:  # pragma: no cover
    return '0x' + bytes_string


def rm_0x_prefix(bytes_string: str) -> str:
    if bytes_string.startswith('0x'):
        return bytes_string[2:]
    return bytes_string


def init_default_logger() -> None:  # pragma: no cover
    handlers = []
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stream_handler = StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    handlers.append(stream_handler)

    logging.basicConfig(level=logging.DEBUG, handlers=handlers)


def chunk(in_string: str, num_chunks: int) -> Generator[str, None, None]:  # pragma: no cover
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


def split_public_key(public_key: str) -> list[bytes]:
    public_key = rm_0x_prefix(public_key)
    pk_parts = list(chunk(public_key, 2))
    return list(map(bytes.fromhex, pk_parts))


def to_camel_case(snake_str: str) -> str:
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def is_test_env() -> bool:
    return 'pytest' in sys.modules or ENV == 'test'
