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

from skale.contracts.base_contract import BaseContract
from skale.contracts.base_contract import transaction_method
from skale.types.dkg import Fp2Point, G2Point, DkgId, KeyShare, VerificationVector, Status, Round
from skale.types.node import NodeId


class DKG(BaseContract):
    def is_node_broadcasted(self, dkg: DkgId, node: NodeId) -> bool:
        return self.contract.functions.isNodeBroadcasted(dkg, node).call()
    
    def is_node_sent_alright(self, dkg: DkgId, node: NodeId) -> bool:
        round_info = self.get_round(dkg)
        return round_info.completed[node]

    def get_participants(self, dkg: DkgId) -> list[NodeId]:
        return self.contract.functions.getParticipants(dkg).call()

    def get_public_key(self, dkg: DkgId) -> G2Point:
        return self.contract.functions.getPublicKey(dkg).call()

    def get_last_dkg_id(self) -> DkgId:
        return DkgId(self.contract.functions.lastDkgId().call())
    
    def get_starting_block_number(self, dkg: DkgId) -> int:
        return self.contract.functions.getStartingBlockNumber(dkg).call()

    def __get_raw_round(self, dkg: DkgId) -> list[Any]:
        return list(self.contract.functions.rounds(dkg).call())

    def get_round(self, dkg: DkgId) -> Round:
        return self._to_round(self.__get_raw_round(dkg))

    def _to_round(self, untyped_round: list[Any]) -> Round:
        return Round(
            id=DkgId(untyped_round[0]),
            status=Status(untyped_round[1]),
            nodes=untyped_round[2],
            publicKey=G2Point(
                x=Fp2Point(a=untyped_round[3][0][0], b=untyped_round[3][0][1]),
                y=Fp2Point(a=untyped_round[3][1][0], b=untyped_round[3][1][1]),
            ),
            startingBlockNumber=untyped_round[4],
            numberOfBroadcasted=untyped_round[5],
            hashedData=untyped_round[6],
            numberOfCompleted=untyped_round[7],
            completed=untyped_round[8],
        )

    @transaction_method
    def alright(self, dkg: DkgId):
        return self.contract.functions.alright(dkg)

    @transaction_method
    def broadcast(
        self,
        dkg: DkgId,
        verification_vector: VerificationVector,
        secret_key_contribution: list[KeyShare],
    ):
        return self.contract.functions.broadcast(dkg, verification_vector, secret_key_contribution)

    @transaction_method
    def generate(self, participants: list[NodeId]):
        return self.contract.functions.generate(participants)
