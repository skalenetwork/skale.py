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
from skale.types.committee import CommitteeGroup, CommitteeIndex
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


def get_nodes_from_last_two_committees(fair: FairManager) -> list[CommitteeGroup]:
    """
    Compose a dictionary with nodes from the last two committees.
    If it is the first committee, it will be saved both
    as first and second committee with first timestamp equal to 0
    """

    latest_committee_index: int = fair.committee.last_committee_index()
    if latest_committee_index == 0:
        committee_a_index: CommitteeIndex = CommitteeIndex(0)
        committee_a = fair.committee.get_committee(CommitteeIndex(0))
        ts_a = 0
    else:
        committee_a_index: CommitteeIndex = CommitteeIndex(latest_committee_index - 1)
        committee_a = fair.committee.get_committee(CommitteeIndex(committee_a_index))
        ts_a = committee_a.starting_timestamp

    staking_contract_address = to_checksum_address(ZERO_ADDRESS)
    if committee_a_index > 0:
        staking_contract_address = to_checksum_address(fair.staking.contract.address)

    committee_a_nodes_data: CommitteeGroup = {
        'index': committee_a_index,
        'ts': ts_a,  # todod: remove, use from committee structure
        'staking_contract_address': staking_contract_address,
        'group': get_committee_nodes(fair, committee_a_index),
        'committee': committee_a,
    }

    committee_b_index = latest_committee_index

    staking_contract_address = to_checksum_address(ZERO_ADDRESS)
    if committee_b_index > 0:
        staking_contract_address = to_checksum_address(fair.staking.contract.address)

    committee_b = fair.committee.get_committee(CommitteeIndex(committee_b_index))
    committee_b_nodes_data: CommitteeGroup = {
        'index': committee_b_index,
        'ts': committee_b.starting_timestamp,  # todod: remove, use from committee structure
        'staking_contract_address': staking_contract_address,
        'group': get_committee_nodes(fair, committee_b_index),
        'committee': fair.committee.get_committee(committee_b_index),
    }

    committee_nodes_data = [committee_a_nodes_data, committee_b_nodes_data]

    return committee_nodes_data
