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

from typing import List

from eth_typing import ChecksumAddress

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.types.node import NodeId


class Staking(BaseContract):
    def get_node_share(self, node: NodeId) -> int:
        return self.contract.functions.getNodeShare(node).call()

    def get_staked_amount(self) -> int:
        return self.contract.functions.getStakedAmount().call()

    def get_staked_to_node_amount(self, node: NodeId) -> int:
        return self.contract.functions.getStakedToNodeAmount(node).call(
            {'from': self.skale.wallet.address}
        )

    def get_staked_nodes(self) -> List[NodeId]:
        return self.contract.functions.getStakedNodes().call()

    def get_earned_fee_amount(self, node: NodeId) -> int:
        return self.contract.functions.getEarnedFeeAmount(node).call()

    def get_staked_amount_for(self, holder: ChecksumAddress) -> int:
        return self.contract.functions.getStakedAmountFor(holder).call()

    def get_staked_nodes_for(self, holder: ChecksumAddress) -> List[NodeId]:
        return self.contract.functions.getStakedNodesFor(holder).call()

    def get_staked_to_node_amount_for(self, node: NodeId, holder: ChecksumAddress) -> int:
        return self.contract.functions.getStakedToNodeAmountFor(node, holder).call()

    @transaction_method
    def stake(self, node: NodeId):
        return self.contract.functions.stake(node)

    @transaction_method
    def retrieve(self, node: NodeId, value: int):
        return self.contract.functions.retrieve(node, value)

    @transaction_method
    def set_fee_rate(self, fee_rate: int):
        return self.contract.functions.setFeeRate(fee_rate)

    @transaction_method
    def claim_fee(self, to: ChecksumAddress, amount: int):
        return self.contract.functions.claimFee(to, amount)

    @transaction_method
    def claim_all_fee(self, to: ChecksumAddress):
        return self.contract.functions.claimAllFee(to)

    @transaction_method
    def disable(self, node: NodeId):
        return self.contract.functions.disable(node)

    @transaction_method
    def enable(self, node: NodeId):
        return self.contract.functions.enable(node)

    def get_reward_wallet(self, node: NodeId) -> ChecksumAddress:
        return self.contract.functions.getRewardWallet(node).call()
