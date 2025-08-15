#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2025-Present SKALE Labs
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

import logging

from skale import FairManager
from skale.types.committee import Committee, CommitteeIndex
from skale.types.dkg import G2Point

logger = logging.getLogger(__name__)

""" This functions are used to generate fair config 'nodeGroups' section data"""


def unpack_bls_public_key(bls_public_key: G2Point) -> dict[str, str]:
    return {
        'blsPublicKey0': str(bls_public_key[0][0]),
        'blsPublicKey1': str(bls_public_key[0][1]),
        'blsPublicKey2': str(bls_public_key[1][0]),
        'blsPublicKey3': str(bls_public_key[1][1]),
    }


def committee_data_to_historical_representation(fair: FairManager, committee: Committee) -> dict:
    bls_public_key = committee.common_public_key
    node_ids = committee.node_ids
    nodes = {}
    for index_in_committee, node_id in enumerate(node_ids):
        public_key = fair.nodes.get_public_key(node_id)
        nodes[node_id] = (
            index_in_committee,
            node_id,
            public_key,
        )
    committee_data = {
        'rotation': None,
        'nodes': nodes,
        'start_ts': committee.starting_timestamp,
        'bls_public_key': unpack_bls_public_key(bls_public_key),
    }

    return committee_data


def generate_committee_history(fair: FairManager) -> dict:
    latest_committee_index: int = fair.committee.last_committee_index()
    committees = {}

    current_finish_ts = None
    for committee_index in reversed(range(0, latest_committee_index + 1)):
        committee = fair.committee.get_committee(CommitteeIndex(committee_index))
        committee_data = committee_data_to_historical_representation(fair, committee)
        committee_data['finish_ts'] = current_finish_ts
        current_finish_ts = committee_data.pop('start_ts')
        committees.update({str(committee_index): committee_data})
    return committees
