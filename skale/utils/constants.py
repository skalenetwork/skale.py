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

NODE_DEPOSIT = 100000000000000000000

GAS = {
    'add_validator': 4500000,
    'create_node': 4500000,
    'create_schain': 7500000,
    'get_bounty': 4500000,
    'send_verdict': 200000,
    'send_verdicts': 500000,
    'set_check_time': 200000,
    'set_latency': 200000,
    'token_transfer': 600000,
    'add_authorized': 100000,
    'set_periods': 200000,
    'delete_node': 6000000,
    'delete_node_by_root': 6000000,
    'delete_schain': 6000000,
    'dkg_broadcast': 8000000,
    'dkg_response': 8000000,
    'dkg_allright': 1000000,
    'dkg_complaint': 1000000,
}

OP_TYPES = {'create_node': 0x1, 'create_schain': 0x10}

LONG_LINE = '=' * 100

SCHAIN_TYPES = {
    'tiny': 1,
    'small': 2,
    'medium': 3,
    'test': 4,
}
