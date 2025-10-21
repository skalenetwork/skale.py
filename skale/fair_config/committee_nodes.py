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

from eth_utils.address import to_checksum_address

from skale.fair_config.utils import convert_to_node_for_chain_config
from skale.fair_manager import FairManager
from skale.types.committee import Committee, CommitteeGroup, CommitteeIndex, Timestamp
from skale.types.node import FairNodeForChainConfig, NodeId, get_ghost_fair_node
from skale.utils.constants import ZERO_ADDRESS

""" This functions are used to generate fair config 'nodes' section data"""


def get_committee_nodes(fair: FairManager, committee_index: int) -> list[FairNodeForChainConfig]:
    committee_nodes = []
    for raw_id in fair.committee.get_committee(CommitteeIndex(committee_index)).node_ids:
        node_id: NodeId = NodeId(raw_id)
        if fair.nodes.active_node_exists(node_id):
            fair_node = fair.nodes.get(node_id)
        else:
            fair_node = get_ghost_fair_node(node_id)
        fair_node_for_config = convert_to_node_for_chain_config(fair, fair_node)
        committee_nodes.append(fair_node_for_config)
    return committee_nodes


def create_committee_group(
    fair: FairManager, committee_index: CommitteeIndex, committee: Committee, timestamp: Timestamp
) -> CommitteeGroup:
    staking_contract_address = to_checksum_address(ZERO_ADDRESS)
    if committee_index > 0:
        staking_contract_address = to_checksum_address(fair.staking.contract.address)
    return {
        'index': committee_index,
        'ts': timestamp,  # todod: remove, use from committee structure
        'staking_contract_address': staking_contract_address,
        'group': get_committee_nodes(fair, committee_index),
        'committee': committee,
    }


def get_nodes_from_two_operational_committees(fair: FairManager) -> list[CommitteeGroup]:
    """
    Compose a dictionary with nodes from the two operational committees.
    If it is the first committee, it will be saved both
    as first and second committee with first timestamp equal to 0
    If there are committee with timestamp in the future two latest committee will be saved.
    Otherwise latest committee will be saved twice.
    """
    latest_committee_index = fair.committee.last_committee_index()
    latest_committee = fair.committee.get_committee(CommitteeIndex(latest_committee_index))

    if latest_committee_index == 0:
        first_index = CommitteeIndex(0)
        first_committee = fair.committee.get_committee(CommitteeIndex(0))
        first_timestamp = Timestamp(0)
    else:
        latest_ts = fair.web3.eth.get_block('latest').get('timestamp', 0)
        first_index = latest_committee_index
        first_committee = latest_committee

        if latest_ts < latest_committee.starting_timestamp:
            previous_committee_index = CommitteeIndex(latest_committee_index - 1)
            previous_committee = fair.committee.get_committee(
                CommitteeIndex(previous_committee_index)
            )
            first_index = previous_committee_index
            first_committee = previous_committee

        first_timestamp = first_committee.starting_timestamp

    second_index = latest_committee_index
    second_committee = latest_committee
    second_timestamp = second_committee.starting_timestamp

    return [
        create_committee_group(fair, first_index, first_committee, first_timestamp),
        create_committee_group(fair, second_index, second_committee, second_timestamp),
    ]
