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

from typing import cast

from skale import MirageManager
from skale.types.committee import Committee
from skale.types.dkg import G2Point
from skale.types.node import NodeId


def unpack_bls_public_key(bls_public_key: G2Point) -> dict[str, int]:
    return {
        'blsPublicKey0': bls_public_key.x.a,
        'blsPublicKey1': bls_public_key.x.b,
        'blsPublicKey2': bls_public_key.y.a,
        'blsPublicKey3': bls_public_key.y.b,
    }


def committee_data_to_node_groups(
    mirage: MirageManager, committee: Committee, committee_index: int
) -> dict:
    committee_data = {}
    bls_public_key = committee.common_public_key
    node_ids = committee.node_ids
    nodes = []
    for node_id, index_in_committee in enumerate(node_ids):
        node = mirage.nodes.get(cast(NodeId, node_id))
        if node is not None:
            nodes.append((index_in_committee, node.id, node.public_key))
    committee_data[str(committee_index)] = committee.node_ids
    committee_data['finish_ts'] = committee.starting_timestamp
    committee_data['bls_public_key'] = unpack_bls_public_key(bls_public_key)
    return committee_data


def get_node_groups(mirage: MirageManager) -> list[dict]:
    latest_committee_index: int = mirage.committee.get_active_committee_index()
    committees = []
    for committee_index in range(latest_committee_index, -1):
        committee = mirage.committee.get_committe(committee_index)
        committee_data = committee_data_to_node_groups(mirage, committee, committee_index)
        committees.append(committee_data)
    return committees
