#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019-Present SKALE Labs
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

from typing import List, Tuple
from eth_typing import ChecksumAddress
from web3.contract.contract import ContractFunction

from skale.contracts.base_contract import transaction_method
from skale.contracts.skale_manager_contract import SkaleManagerContract
from skale.transactions.tools import retry_tx
from skale.types.dkg import G2Point, KeyShare, VerificationVector
from skale.types.node import NodeId
from skale.types.schain import SchainHash


class DKG(SkaleManagerContract):
    @retry_tx
    @transaction_method
    def broadcast(
        self,
        group_index: SchainHash,
        node_index: NodeId,
        verification_vector: VerificationVector,
        secret_key_contribution: List[KeyShare],
        rotation_id: int,
    ) -> 'ContractFunction':
        return self.contract.functions.broadcast(
            group_index, node_index, verification_vector, secret_key_contribution, rotation_id
        )

    @retry_tx
    @transaction_method
    def pre_response(
        self,
        group_index: SchainHash,
        from_node_index: NodeId,
        verification_vector: VerificationVector,
        verification_vector_mult: VerificationVector,
        secret_key_contribution: List[KeyShare],
    ) -> 'ContractFunction':
        return self.contract.functions.preResponse(
            group_index,
            fromNodeIndex=from_node_index,
            verificationVector=verification_vector,
            verificationVectorMultiplication=verification_vector_mult,
            secretKeyContribution=secret_key_contribution,
        )

    @retry_tx
    @transaction_method
    def response(
        self,
        group_index: SchainHash,
        from_node_index: NodeId,
        secret_number: int,
        multiplied_share: G2Point,
    ) -> 'ContractFunction':
        return self.contract.functions.response(
            group_index,
            fromNodeIndex=from_node_index,
            secretNumber=secret_number,
            multipliedShare=multiplied_share,
        )

    @retry_tx
    @transaction_method
    def alright(self, group_index: SchainHash, from_node_index: NodeId) -> 'ContractFunction':
        return self.contract.functions.alright(group_index, from_node_index)

    @retry_tx
    @transaction_method
    def complaint(
        self, group_index: SchainHash, from_node_index: NodeId, to_node_index: NodeId
    ) -> 'ContractFunction':
        return self.contract.functions.complaint(group_index, from_node_index, to_node_index)

    @retry_tx
    @transaction_method
    def complaint_bad_data(
        self, group_index: SchainHash, from_node_index: NodeId, to_node_index: NodeId
    ) -> 'ContractFunction':
        return self.contract.functions.complaintBadData(group_index, from_node_index, to_node_index)

    def is_last_dkg_successful(self, group_index: SchainHash) -> bool:
        return bool(self.contract.functions.isLastDKGSuccessful(group_index).call())

    def is_channel_opened(self, group_index: SchainHash) -> bool:
        return bool(self.contract.functions.isChannelOpened(group_index).call())

    def is_broadcast_possible(
        self, group_index: SchainHash, node_id: NodeId, address: ChecksumAddress
    ) -> bool:
        return bool(
            self.contract.functions.isBroadcastPossible(group_index, node_id).call(
                {'from': address}
            )
        )

    def is_alright_possible(
        self, group_index: SchainHash, node_id: NodeId, address: ChecksumAddress
    ) -> bool:
        return bool(
            self.contract.functions.isAlrightPossible(group_index, node_id).call({'from': address})
        )

    def is_complaint_possible(
        self, group_index: SchainHash, node_from: NodeId, node_to: NodeId, address: ChecksumAddress
    ) -> bool:
        return bool(
            self.contract.functions.isComplaintPossible(group_index, node_from, node_to).call(
                {'from': address}
            )
        )

    def is_pre_response_possible(
        self, group_index: SchainHash, node_id: NodeId, address: ChecksumAddress
    ) -> bool:
        return bool(
            self.contract.functions.isPreResponsePossible(group_index, node_id).call(
                {'from': address}
            )
        )

    def is_response_possible(
        self, group_index: SchainHash, node_id: NodeId, address: ChecksumAddress
    ) -> bool:
        return bool(
            self.contract.functions.isResponsePossible(group_index, node_id).call({'from': address})
        )

    def is_all_data_received(self, group_index: SchainHash, node_from: NodeId) -> bool:
        return bool(self.contract.functions.isAllDataReceived(group_index, node_from).call())

    def is_everyone_broadcasted(self, group_index: SchainHash, address: ChecksumAddress) -> bool:
        return bool(
            self.contract.functions.isEveryoneBroadcasted(group_index).call({'from': address})
        )

    def get_number_of_completed(self, group_index: SchainHash) -> int:
        return int(self.contract.functions.getNumberOfCompleted(group_index).call())

    def get_channel_started_time(self, group_index: SchainHash) -> int:
        return int(self.contract.functions.getChannelStartedTime(group_index).call())

    def get_complaint_started_time(self, group_index: SchainHash) -> int:
        return int(self.contract.functions.getComplaintStartedTime(group_index).call())

    def get_alright_started_time(self, group_index: SchainHash) -> int:
        return int(self.contract.functions.getAlrightStartedTime(group_index).call())

    def get_complaint_data(self, group_index: SchainHash) -> Tuple[NodeId, NodeId]:
        return tuple(self.contract.functions.getComplaintData(group_index).call())

    def get_time_of_last_successful_dkg(self, group_index: SchainHash) -> int:
        return int(self.contract.functions.getTimeOfLastSuccessfulDKG(group_index).call())

    def is_node_broadcasted(self, group_index: SchainHash, node_id: NodeId) -> bool:
        return bool(self.contract.functions.isNodeBroadcasted(group_index, node_id).call())
