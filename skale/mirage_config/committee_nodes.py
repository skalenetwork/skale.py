from typing import cast

from skale.mirage_manager import MirageManager
from skale.types.committee import CommitteeGroup, CommitteeIndex
from skale.types.node import MirageNode, NodeId

""" This functions are used to generate mirage config 'nodes' section data"""


def get_committee_nodes(mirage: MirageManager, committee_index: int) -> list[MirageNode]:
    return [
        mirage.nodes.get(cast(NodeId, node_id))
        for node_id in mirage.committee.get_committee(
            cast(CommitteeIndex, committee_index)
        ).node_ids
    ]


def get_nodes_from_last_two_committees(mirage: MirageManager) -> list[CommitteeGroup]:
    """
    Compose a dictionary with nodes from the last two committees.
    If it is the first committee, it will be saved both
    as first and second committee with first timestamp equal to 0
    """

    latest_committee_index: int = mirage.committee.get_active_committee_index()
    if latest_committee_index == 0:
        committee_a_index: CommitteeIndex = cast(CommitteeIndex, 0)
        ts_a = 0
    else:
        committee_a_index: CommitteeIndex = cast(CommitteeIndex, latest_committee_index - 1)
        ts_a = mirage.committee.get_committee(
            cast(CommitteeIndex, committee_a_index)
        ).starting_timestamp
    committee_a_nodes_data: dict = {
        'index': committee_a_index,
        'ts': ts_a,
        'group': get_committee_nodes(mirage, committee_a_index),
    }

    committee_b_index = latest_committee_index
    ts_b = mirage.committee.get_committee(
        cast(CommitteeIndex, committee_b_index)
    ).starting_timestamp
    committee_b_nodes_data: CommitteeGroup = {
        'index': committee_b_index,
        'ts': ts_b,
        'group': get_committee_nodes(mirage, committee_b_index),
    }

    committee_nodes_data = [committee_a_nodes_data, committee_b_nodes_data]

    return committee_nodes_data
