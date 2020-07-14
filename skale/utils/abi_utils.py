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

from skale.utils.exceptions import IncompatibleAbiError


def get_abi_key_name(contract_name):
    # todo: tmp fix for inconsistent contract names
    if contract_name == 'manager' or contract_name == 'token':
        return f'skale_{contract_name}_abi'
    if contract_name == 'dkg':
        return 'skale_d_k_g_abi'
    return f'{contract_name}_abi'


def get_address_key_name(contract_name):
    if contract_name == 'manager' or contract_name == 'token':
        return f'skale_{contract_name}_address'
    if contract_name == 'dkg':
        return 'skale_d_k_g_address'
    return f'{contract_name}_address'


def get_abi_key(abi, key):
    try:
        return abi[key]
    except KeyError:
        raise IncompatibleAbiError(key)


def get_contract_address_by_name(abi, name):
    return get_abi_key(abi, get_address_key_name(name))


def get_contract_abi_by_name(abi, name):
    return get_abi_key(abi, get_abi_key_name(name))
