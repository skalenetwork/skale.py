"""SKALE node rotation test"""

import json
import logging
import os

from skale.contracts.manager.nodes import NodeStatus
from skale.types.dkg import Fp2Point, G2Point, KeyShare
from skale.utils.contracts_provision.fair import set_up_nodes
from skale.utils.contracts_provision.main import _skip_evm_time

logger = logging.getLogger(__name__)


TEST_ROTATION_DELAY = 45260

DIR = os.path.dirname(os.path.realpath(__file__))
DKG_DATA_PATH = os.path.join(DIR, 'dkg_data.json')

with open(DKG_DATA_PATH) as data_file:
    TEST_DKG_DATA = json.loads(data_file.read())


def send_broadcasts(nodes, skale_instances, group_index, skip_node_index=None, rotation_id=0):
    for i, node in enumerate(nodes):
        if i != skip_node_index:
            verification_vector = [
                G2Point(*[Fp2Point(*fp2_point) for fp2_point in g2_point])
                for g2_point in TEST_DKG_DATA['test_verification_vectors'][i]
            ]
            secret_key_contribution = [
                KeyShare(tuple(key_share[0]), key_share[1])
                for key_share in TEST_DKG_DATA['test_encrypted_secret_key_contributions'][i]
            ]
            skale_instances[i].dkg.broadcast(
                group_index,
                node['node_id'],
                verification_vector,
                secret_key_contribution,
                rotation_id,
            )
        else:
            print(f'Skipping broadcast from node {node["node_id"]}')


def send_alrights(nodes, skale_instances, group_index):
    for i, node in enumerate(nodes):
        skale_instances[i].dkg.alright(group_index, node['node_id'])


def send_complaint(nodes, skale_instances, group_index, failed_node_index):
    for i, skale_instance in enumerate(skale_instances):
        if i != failed_node_index:
            failed_node_id = nodes[failed_node_index]['node_id']
            skale_instance.dkg.complaint(group_index, nodes[i]['node_id'], failed_node_id)


def rotate_node(
    skale, group_index, nodes, skale_instances, exiting_node_index, do_dkg=True, rotation_id=0
):
    new_nodes, new_skale_instances = set_up_nodes(skale, 1, no_zero_id=False)
    skale.nodes.init_exit(nodes[exiting_node_index]['node_id'])
    skale_instances[exiting_node_index].manager.node_exit(nodes[exiting_node_index]['node_id'])
    nodes[exiting_node_index] = new_nodes[0]
    skale_instances[exiting_node_index] = new_skale_instances[0]
    if do_dkg:
        run_dkg(nodes, skale_instances, group_index, rotation_id=rotation_id)
    return nodes, skale_instances


def fail_dkg(
    skale,
    nodes,
    skale_instances,
    group_index,
    failed_node_index,
    second_failed_node_index=None,
    rotation_id=0,
) -> list:
    logger.info('Failing first DKG...')
    new_node_ids = []
    new_nodes, new_skale_instances = set_up_nodes(skale, 1, no_zero_id=False)
    new_node_ids.append(new_nodes[0]['node_id'])

    send_broadcasts(nodes, skale_instances, group_index, failed_node_index, rotation_id=rotation_id)
    _skip_evm_time(skale_instances[0].web3, skale.constants_holder.get_dkg_timeout())
    send_complaint(nodes, skale_instances, group_index, failed_node_index)

    nodes[failed_node_index] = new_nodes[0]
    skale_instances[failed_node_index] = new_skale_instances[0]

    if second_failed_node_index:
        logger.info('Failing second DKG...')
        new_nodes, new_skale_instances = set_up_nodes(skale, 1, no_zero_id=False)
        new_node_ids.append(new_nodes[0]['node_id'])

        send_broadcasts(
            nodes,
            skale_instances,
            group_index,
            second_failed_node_index,
            rotation_id=rotation_id + 1,
        )
        _skip_evm_time(skale_instances[0].web3, skale.constants_holder.get_dkg_timeout())
        send_complaint(nodes, skale_instances, group_index, second_failed_node_index)

        nodes[second_failed_node_index] = new_nodes[0]
        skale_instances[second_failed_node_index] = new_skale_instances[0]

    run_dkg(
        nodes,
        skale_instances,
        group_index,
        rotation_id=rotation_id + 1 + (0 if second_failed_node_index is None else 1),
    )
    return new_node_ids


def run_dkg(nodes, skale_instances, group_index, skip_time=True, rotation_id=0):
    logger.info('Running DKG procedure...')
    send_broadcasts(nodes, skale_instances, group_index, rotation_id=rotation_id)
    send_alrights(nodes, skale_instances, group_index)
    if skip_time:
        _skip_evm_time(skale_instances[0].web3, TEST_ROTATION_DELAY)


def remove_node(skale, node_id):
    if skale.nodes.get_node_status(node_id) == NodeStatus.IN_MAINTENANCE:
        skale.nodes.remove_from_in_maintenance(node_id)
    if skale.nodes.get_node_status(node_id) != NodeStatus.LEFT:
        skale.nodes.init_exit(node_id)
        skale.manager.node_exit(node_id)
