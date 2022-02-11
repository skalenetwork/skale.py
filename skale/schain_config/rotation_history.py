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

import logging
from collections import namedtuple

from skale import Skale
from skale.contracts.manager.node_rotation import Rotation

logger = logging.getLogger(__name__)

RotationNodeData = namedtuple('RotationNodeData', ['index', 'node_id', 'public_key'])


def get_previous_schain_groups(skale, schain_name: str, leaving_node_id=None) -> dict:
    """
    Returns all previous node groups with public keys and finish timestamps.
    In case of no rotations returns the current state.
    """
    logger.info(f'Collecting rotation history for {schain_name}...')
    node_groups = {}

    group_id = skale.schains.name_to_group_id(schain_name)
    previous_public_keys = skale.key_storage.get_all_previous_public_keys(group_id)
    current_public_key = skale.key_storage.get_common_public_key(group_id)

    rotation = skale.node_rotation.get_rotation_obj(schain_name)

    logger.info(f'Rotation data for {schain_name}: {rotation}')

    _add_current_schain_state(skale, node_groups, rotation, schain_name, current_public_key)
    if rotation.rotation_counter == 0:
        return node_groups

    _add_previous_schain_rotations_state(
        skale, node_groups, rotation, schain_name, previous_public_keys, leaving_node_id)
    return node_groups


def _add_current_schain_state(
    skale: Skale,
    node_groups: dict,
    rotation: Rotation,
    schain_name: str,
    current_public_key: list
) -> dict:
    """
    Internal function, composes the initial info about the current sChain state and adds it to the
    node_groups dictionary
    """
    current_nodes = {}
    ids = skale.schains_internal.get_node_ids_for_schain(schain_name)
    for (index, node_id) in enumerate(ids):
        public_key = skale.nodes.get_node_public_key(node_id)
        current_nodes[node_id] = RotationNodeData(index, node_id, public_key)

    node_groups[rotation.rotation_counter] = {
        'rotation': None,
        'nodes': current_nodes,
        'finish_ts': None,
        'bls_public_key': _compose_bls_public_key_info(current_public_key)
    }


def _add_previous_schain_rotations_state(
    skale: Skale,
    node_groups: dict,
    rotation: Rotation,
    schain_name: str,
    previous_public_keys: list,
    leaving_node_id=None
) -> dict:
    """
    Internal function, handles rotations from (rotation_counter - 2) to 0 and adds them to the
    node_groups dictionary
    """
    previous_nodes = {}

    for rotation_id in range(rotation.rotation_counter - 1, -1, -1):
        nodes = node_groups[rotation_id + 1]['nodes'].copy()
        for node_id in nodes:
            if node_id not in previous_nodes:
                previous_node = skale.node_rotation.get_previous_node(schain_name, node_id)
                if previous_node is not None:
                    finish_ts = skale.node_rotation.get_schain_finish_ts(previous_node, schain_name)
                    previous_nodes[node_id] = {
                        'finish_ts': finish_ts,
                        'previous_node_id': previous_node
                    }

        latest_exited_node_id = max(previous_nodes.items(), key=lambda x: x[1]['finish_ts'])[0]
        previous_node_id = previous_nodes[latest_exited_node_id]['previous_node_id']
        public_key = skale.nodes.get_node_public_key(previous_node_id)

        nodes[previous_node_id] = RotationNodeData(
            nodes[latest_exited_node_id].index,
            previous_node_id,
            public_key
        )
        del nodes[latest_exited_node_id]

        is_node_in_exceptions = skale.schains_internal.check_exception(
            schain_name,
            previous_node_id
        )

        if not is_node_in_exceptions:
            bls_public_key = _pop_previous_bls_public_key(previous_public_keys)
            node_finish_ts = previous_nodes[latest_exited_node_id]['finish_ts']
        else:
            bls_public_key, node_finish_ts = None, None

        logger.info(f'Adding rotation: {previous_node_id} -> {latest_exited_node_id}')

        node_groups[rotation_id] = {
            'rotation': {
                'leaving_node_id': previous_node_id,
                'new_node_id': latest_exited_node_id
            },
            'nodes': nodes,
            'finish_ts': node_finish_ts,
            'bls_public_key': bls_public_key
        }

        del previous_nodes[latest_exited_node_id]

        if leaving_node_id and previous_node_id == leaving_node_id:
            logger.info(f'Finishing rotation history parsing: {leaving_node_id} found')
            break


def _pop_previous_bls_public_key(previous_public_keys):
    """
    Returns BLS public key for the group and removes it from the list, returns None if node
    with provided node_id was kicked out of the chain because of failed DKG.
    """
    raw_bls_keys = previous_public_keys[-1]
    bls_keys = _compose_bls_public_key_info(raw_bls_keys)
    del previous_public_keys[-1]
    return bls_keys


def _compose_bls_public_key_info(bls_public_key: str) -> dict:
    return {
        'blsPublicKey0': str(bls_public_key[0][0]),
        'blsPublicKey1': str(bls_public_key[0][1]),
        'blsPublicKey2': str(bls_public_key[1][0]),
        'blsPublicKey3': str(bls_public_key[1][1])
    }


def get_new_nodes_list(skale: Skale, name: str, node_groups) -> list:
    """Returns list of new nodes in for the latest rotation"""
    logger.info(f'Getting new nodes list for chain {name}')
    rotation = skale.node_rotation.get_rotation_obj(name)
    current_group_ids = node_groups[rotation.rotation_counter]['nodes'].keys()
    new_nodes = []
    for index in node_groups:
        past_rotation = node_groups[index]['rotation']
        if not past_rotation:
            continue
        if past_rotation['new_node_id'] in current_group_ids:
            new_nodes.append(past_rotation['new_node_id'])
        else:
            logger.info(f'{past_rotation["new_node_id"]} NOT IN {current_group_ids}')
        if rotation.leaving_node_id == past_rotation['leaving_node_id']:
            break
    logger.info(f'New nodes list for chain {name}: {new_nodes}')
    return new_nodes
