#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2021-Present SKALE Labs
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

from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Dict, List, TypedDict
from skale.types.rotation import RotationNodeData

if TYPE_CHECKING:
    from skale.skale_manager import SkaleManager
    from skale.types.dkg import G2Point
    from skale.types.node import NodeId
    from skale.types.rotation import BlsPublicKey, NodesGroup, Rotation
    from skale.types.schain import SchainName

logger = logging.getLogger(__name__)


class PreviousNodeData(TypedDict):
    finish_ts: int
    previous_node_id: NodeId


def get_previous_schain_groups(
    skale: SkaleManager,
    schain_name: SchainName,
    leaving_node_id: NodeId | None = None,
) -> Dict[int, NodesGroup]:
    """
    Returns all previous node groups with public keys and finish timestamps.
    In case of no rotations returns the current state.
    """
    logger.info(f'Collecting rotation history for {schain_name}...')
    node_groups: dict[int, NodesGroup] = {}

    group_id = skale.schains.name_to_id(schain_name)

    previous_public_keys = skale.key_storage.get_all_previous_public_keys(group_id)
    current_public_key = skale.key_storage.get_common_public_key(group_id)

    rotation = skale.node_rotation.get_rotation(schain_name)

    logger.info(f'Rotation data for {schain_name}: {rotation}')

    _add_current_schain_state(skale, node_groups, rotation, schain_name, current_public_key)
    if rotation.rotation_counter == 0:
        return node_groups

    _add_previous_schain_rotations_state(
        skale=skale,
        node_groups=node_groups,
        rotation=rotation,
        schain_name=schain_name,
        previous_public_keys=previous_public_keys,
        leaving_node_id=leaving_node_id,
    )

    return node_groups


def _add_current_schain_state(
    skale: SkaleManager,
    node_groups: dict[int, NodesGroup],
    rotation: Rotation,
    schain_name: SchainName,
    current_public_key: G2Point,
) -> None:
    """
    Internal function, composes the initial info about the current sChain state and adds it to the
    node_groups dictionary
    """
    current_nodes = {}
    ids = skale.schains_internal.get_node_ids_for_schain(schain_name)
    for index, node_id in enumerate(ids):
        public_key = skale.nodes.get_node_public_key(node_id)
        current_nodes[node_id] = RotationNodeData(index, node_id, public_key)

    node_groups[rotation.rotation_counter] = {
        'rotation': None,
        'nodes': current_nodes,
        'finish_ts': None,
        'bls_public_key': _compose_bls_public_key_info(current_public_key),
    }


def _add_previous_schain_rotations_state(
    skale: SkaleManager,
    node_groups: dict[int, NodesGroup],
    rotation: Rotation,
    schain_name: SchainName,
    previous_public_keys: list[G2Point],
    leaving_node_id: NodeId | None = None,
) -> None:
    """
    Internal function, handles rotations from (rotation_counter - 2) to 0 and adds them to the
    node_groups dictionary
    """

    previous_nodes: Dict[NodeId, PreviousNodeData] = {}

    for rotation_id in range(rotation.rotation_counter - 1, -1, -1):
        nodes = node_groups[rotation_id + 1]['nodes'].copy()
        for node_id in nodes:
            if node_id not in previous_nodes:
                previous_node = skale.node_rotation.get_previous_node(schain_name, node_id)
                if previous_node is not None:
                    finish_ts = skale.node_rotation.get_schain_finish_ts(previous_node, schain_name)
                    previous_nodes[node_id] = {
                        'finish_ts': finish_ts or 0,
                        'previous_node_id': previous_node,
                    }

        new_node_id = max(previous_nodes.items(), key=lambda x: x[1]['finish_ts'])[0]
        previous_node_id = previous_nodes[new_node_id]['previous_node_id']
        public_key = skale.nodes.get_node_public_key(previous_node_id)

        current_finish_ts = previous_nodes[new_node_id]['finish_ts']
        next_dkg_is_failed = current_finish_ts + 1 == node_groups[rotation_id + 1]['finish_ts']

        nodes[previous_node_id] = RotationNodeData(
            nodes[new_node_id].index, previous_node_id, public_key
        )
        del nodes[new_node_id]

        bls_public_key = None
        if not next_dkg_is_failed:
            if len(previous_public_keys) > 0:
                bls_public_key = _pop_previous_bls_public_key(previous_public_keys)
        else:
            bls_public_key = node_groups[rotation_id + 1]['bls_public_key']
            node_groups[rotation_id + 1]['finish_ts'] = None
            node_groups[rotation_id + 1]['bls_public_key'] = None

        logger.info(f'Adding rotation: {previous_node_id} -> {new_node_id}')

        node_groups[rotation_id] = {
            'rotation': {'leaving_node_id': previous_node_id, 'new_node_id': new_node_id},
            'nodes': nodes,
            'finish_ts': current_finish_ts,
            'bls_public_key': bls_public_key,
        }

        del previous_nodes[new_node_id]

        if leaving_node_id and previous_node_id == leaving_node_id:
            logger.info(f'Finishing rotation history parsing: {leaving_node_id} found')
            break


def _pop_previous_bls_public_key(previous_public_keys: List[G2Point]) -> BlsPublicKey | None:
    """
    Returns BLS public key for the group and removes it from the list, returns None if node
    with provided node_id was kicked out of the chain because of failed DKG.
    """
    raw_bls_keys = previous_public_keys[-1]
    bls_keys = _compose_bls_public_key_info(raw_bls_keys)
    del previous_public_keys[-1]
    return bls_keys


def _compose_bls_public_key_info(bls_public_key: G2Point) -> BlsPublicKey | None:
    if bls_public_key:
        return {
            'blsPublicKey0': str(bls_public_key[0][0]),
            'blsPublicKey1': str(bls_public_key[0][1]),
            'blsPublicKey2': str(bls_public_key[1][0]),
            'blsPublicKey3': str(bls_public_key[1][1]),
        }
    return None
