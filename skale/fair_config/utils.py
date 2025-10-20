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

from skale.fair_manager import FairManager
from skale.types.committee import CommitteeIndex
from skale.types.node import FairNode, FairNodeForChainConfig
from skale.utils.constants import ZERO_ADDRESS


def convert_to_node_for_chain_config(fair: FairManager, node: FairNode) -> FairNodeForChainConfig:
    reward_wallet_address = fair.web3.to_checksum_address(ZERO_ADDRESS)
    # Checking if the node is in boot node group i.e. is in the initial committee
    initial_committee_index: CommitteeIndex = CommitteeIndex(0)
    initial_committee = fair.committee.get_committee(initial_committee_index)
    public_key = fair.nodes.get_public_key(node.id)
    if node.id not in initial_committee.node_ids:
        reward_wallet_address = fair.staking.get_reward_wallet(node.id)
    return FairNodeForChainConfig(
        **node.to_dict(),
        ip=node.ip,
        reward_wallet_address=reward_wallet_address,
        public_key=public_key,
    )
