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

from secrets import randbelow, choice
import string


def generate_random_ip():
    return '.'.join('%s' % randbelow(255) for _ in range(4))


def generate_random_name(len=8):
    return ''.join(
        choice(string.ascii_uppercase + string.digits) for _ in range(len)
    )


def generate_random_port():
    return randbelow(60000)


def generate_random_node_data():
    return generate_random_ip(), generate_random_ip(), \
        generate_random_port(), generate_random_name()


def generate_random_schain_data(skale):
    schain_type = skale.schains_internal.number_of_schain_types()
    lifetime_seconds = 3600  # 1 hour
    return schain_type, lifetime_seconds, generate_random_name()
