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

from typing import Any

from eth_typing import ChecksumAddress

from skale.contracts.base_contract import BaseContract
from skale.contracts.base_contract import transaction_method
from skale.types.committee import Committee as CommitteeStruct, CommitteeIndex
from skale.types.node import NodeId


class Committee(BaseContract):
    def __get_raw(self, committee_index: CommitteeIndex) -> list[Any]:
        return list(self.contract.functions.getCommittee(committee_index).call())

    def get_committee(self, committee_index: CommitteeIndex) -> CommitteeStruct:
        return self._to_committee(self.__get_raw(committee_index))

    def _to_committee(self, untyped_committee: list[Any]) -> CommitteeStruct:
        return CommitteeStruct(
            node_ids=untyped_committee[0],
            dkg_id=untyped_committee[1],
            common_public_key=untyped_committee[2],
            starting_timestamp=untyped_committee[3],
        )

    def is_node_in_current_or_next_committee(self, node: NodeId) -> bool:
        return self.contract.functions.isNodeInCurrentOrNextCommittee(node).call()

    def get_active_committee_index(self) -> CommitteeIndex:
        return CommitteeIndex(self.contract.functions.getActiveCommitteeIndex().call())

    @transaction_method
    def select(self):
        return self.contract.functions.select()

    @transaction_method
    def set_dkg(self, dkg_address: ChecksumAddress):
        return self.contract.functions.setDkg(dkg_address)

    @transaction_method
    def set_nodes(self, nodes_address: ChecksumAddress):
        return self.contract.functions.setNodes(nodes_address)

    @transaction_method
    def set_status(self, status_address: ChecksumAddress):
        return self.contract.functions.setStatus(status_address)

    @transaction_method
    def set_staking(self, staking_address: ChecksumAddress):
        return self.contract.functions.setStaking(staking_address)

    @transaction_method
    def set_version(self, new_version: str):
        return self.contract.functions.setVersion(new_version)

    @transaction_method
    def set_committee_size(self, size: int):
        return self.contract.functions.setCommitteeSize(size)

    @transaction_method
    def set_transition_delay(self, delay: int):
        return self.contract.functions.setTransitionDelay(delay)
