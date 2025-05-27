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
from skale.types.dkg import G2Point, DkgId, KeyShare, VerificationVector
from skale.types.node import NodeId


class DKG(BaseContract):
    def is_node_broadcasted(self, dkg: DkgId, node: NodeId) -> bool:
        return self.contract.functions.isNodeBroadcasted(dkg, node).call()

    def get_participants(self, dkg: DkgId) -> list[NodeId]:
        return self.contract.functions.getParticipants(dkg).call()

    def get_public_key(self, dkg: DkgId) -> G2Point:
        return self.contract.functions.getPublicKey(dkg).call()

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
