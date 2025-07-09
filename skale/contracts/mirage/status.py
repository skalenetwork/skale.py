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

from skale.contracts.base_contract import BaseContract
from skale.contracts.base_contract import transaction_method
from skale.types.node import NodeId
from skale.types.committee import Timestamp


class Status(BaseContract):
    def last_heartbeat_timestamp(self, node_id: NodeId) -> Timestamp:
        return self.contract.functions.lastHeartbeatTimestamp(node_id).call()

    def heartbeat_interval(self) -> int:
        return self.contract.functions.heartbeatInterval().call()

    def is_healthy(self, node_id: NodeId) -> bool:
        return self.contract.functions.isHealthy(node_id).call()

    def get_nodes_eligible_for_committee(self) -> list[NodeId]:
        return self.contract.functions.getNodesEligibleForCommittee().call()

    def get_whitelisted_nodes(self) -> list[NodeId]:
        return self.contract.functions.getWhitelistedNodes().call()

    def is_whitelisted(self, node_id: NodeId) -> bool:
        return self.contract.functions.isWhitelisted(node_id).call()

    @transaction_method
    def alive(self):
        return self.contract.functions.alive()

    @transaction_method
    def set_heartbeat_interval(self, interval: int):
        return self.contract.functions.setHeartbeatInterval(interval)

    @transaction_method
    def whitelist_node(self, node_id: NodeId):
        return self.contract.functions.whitelistNode(node_id)

    @transaction_method
    def remove_node_from_whitelist(self, node_id: NodeId):
        return self.contract.functions.removeNodeFromWhitelist(node_id)
