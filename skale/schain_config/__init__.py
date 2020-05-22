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

# flake8: noqa: E402, F401

SCHAIN_OWNER_ALLOC = 1000000000000000000000  # todo: tmp!
NODE_OWNER_ALLOC = 1000000000000000000000  # todo: tmp!

PORTS_PER_SCHAIN = 11

PRECOMPILED_IMA_CONTRACTS = {
    'skale_features': {
        'filename': 'SkaleFeatures'
    },
    'lock_and_data_for_schain': {
        'filename': 'LockAndDataForSchain'
    },
    'eth_erc20': {
        'filename': 'EthERC20'
    },
    'token_manager': {
        'filename': 'TokenManager'
    },
    'lock_and_data_for_schain_erc20': {
        'filename': 'LockAndDataForSchainERC20'
    },
    'erc20_module_for_schain': {
        'filename': 'ERC20ModuleForSchain'
    },
    'lock_and_data_for_schain_erc721': {
        'filename': 'LockAndDataForSchainERC721'
    },
    'erc721_module_for_schain': {
        'filename': 'ERC721ModuleForSchain'
    },
    'token_factory': {
        'filename': 'TokenFactory'
    },
    'message_proxy_chain': {
        'filename': 'MessageProxyForSchain'
    }
}

from skale.schain_config.generator import generate_skale_schain_config
