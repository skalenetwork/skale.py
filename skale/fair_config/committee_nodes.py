from skale.fair_manager import FairManager
from skale.types.committee import CommitteeGroup, CommitteeIndex
from skale.types.node import FairNode, NodeId

""" This functions are used to generate fair config 'nodes' section data"""


def get_committee_nodes(fair: FairManager, committee_index: int) -> list[FairNode]:
    return [
        fair.nodes.get(NodeId(node_id))
        for node_id in fair.committee.get_committee(CommitteeIndex(committee_index)).node_ids
    ]


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
    committee_a_nodes_data: CommitteeGroup = {
        'index': committee_a_index,
        'ts': ts_a,  # todod: remove, use from committee structure
        'group': get_committee_nodes(fair, committee_a_index),
        'committee': committee_a,
    }

    committee_b_index = latest_committee_index

    committee_b = fair.committee.get_committee(CommitteeIndex(committee_b_index))
    committee_b_nodes_data: CommitteeGroup = {
        'index': committee_b_index,
        'ts': committee_b.starting_timestamp,  # todod: remove, use from committee structure
        'group': get_committee_nodes(fair, committee_b_index),
        'committee': fair.committee.get_committee(committee_b_index),
    }

    committee_nodes_data = [committee_a_nodes_data, committee_b_nodes_data]

    return committee_nodes_data
