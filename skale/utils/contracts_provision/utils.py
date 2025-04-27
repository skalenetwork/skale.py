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

import random
import string

from skale.skale_manager import SkaleManager
from skale.types.node import Port
from skale.types.schain import SchainName


def generate_random_ip() -> str:
    return '.'.join('%s' % random.randint(0, 255) for i in range(4))


def generate_random_name(length: int = 8) -> SchainName:
    return SchainName(''.join(random.choices(string.ascii_uppercase + string.digits, k=length)))


def generate_random_port() -> Port:
    return Port(random.randint(0, 60000))


def generate_random_node_data() -> tuple[str, str, int, str]:
    return (
        generate_random_ip(),
        generate_random_ip(),
        generate_random_port(),
        generate_random_name(),
    )


def generate_random_schain_data(skale: SkaleManager) -> tuple[int, int, SchainName]:
    schain_type = skale.schains_internal.number_of_schain_types()
    lifetime_seconds = 3600  # 1 hour
    return schain_type, lifetime_seconds, generate_random_name()
