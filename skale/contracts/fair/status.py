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

import functools
import logging
import math

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.contracts.fair.nodes import Nodes
from skale.types.committee import Timestamp
from skale.types.node import NodeId

logger = logging.getLogger(__name__)


class Status(BaseContract):
    @property
    @functools.lru_cache()
    def nodes(self) -> 'Nodes':
        return self.skale.nodes

    def last_heartbeat_timestamp(self, node_id: NodeId) -> Timestamp:
        return self.contract.functions.lastHeartbeatTimestamp(node_id).call()

    def heartbeat_interval(self) -> int:
        return self.contract.functions.heartbeatInterval().call()

    def is_healthy(self, node_id: NodeId) -> bool:
        return self.contract.functions.isHealthy(node_id).call()

    def get_whitelisted_nodes(self) -> list[NodeId]:
        return self.contract.functions.getWhitelistedNodes().call()

    def is_whitelisted(self, node_id: NodeId) -> bool:
        return self.contract.functions.isWhitelisted(node_id).call()

    def active_whitelisted_node_ids(self) -> list[NodeId]:
        return list(set(self.nodes.get_active_node_ids()) & set(self.get_whitelisted_nodes()))

    def calc_alive_gas_limit(self) -> int:
        active_whitelisted_nodes = len(self.active_whitelisted_node_ids())
        alive_gas_limit_float = (230000 * math.log10(active_whitelisted_nodes + 15) + 420000) * 1.2
        alive_gas_limit = int(alive_gas_limit_float)
        logger.info(
            'alive_gas_limit: %s, active_whitelisted_nodes: %s',
            alive_gas_limit,
            active_whitelisted_nodes,
        )
        return alive_gas_limit

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
