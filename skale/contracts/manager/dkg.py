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

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.tools import retry_tx
from skale.utils.helper import split_public_key


class KeyShare:
    def __init__(self, public_key: str, share: bytes):
        self.public_key = split_public_key(public_key)
        self.share = share
        self.tuple = (self.public_key, self.share)


class G2Point:
    def __init__(self, xa, xb, ya, yb):
        self.x = (xa, xb)
        self.y = (ya, yb)
        self.tuple = (self.x, self.y)


class DKG(BaseContract):
    @retry_tx
    @transaction_method
    def broadcast(self, group_index, node_index,
                  verification_vector, secret_key_contribution):
        return self.contract.functions.broadcast(group_index, node_index,
                                                 verification_vector,
                                                 secret_key_contribution)

    @retry_tx
    @transaction_method
    def pre_response(
        self,
        group_index: str,
        from_node_index: int,
        verification_vector: list,
        verification_vector_mult: list,
        secret_key_contribution: list
    ):
        return self.contract.functions.preResponse(
            schainId=group_index,
            fromNodeIndex=from_node_index,
            verificationVector=verification_vector,
            verificationVectorMult=verification_vector_mult,
            secretKeyContribution=secret_key_contribution,
        )

    @retry_tx
    @transaction_method
    def response(
            self,
            group_index: bytes,
            from_node_index: int,
            secret_number: int,
            multiplied_share: G2Point
    ):
        return self.contract.functions.response(
            schainId=group_index,
            fromNodeIndex=from_node_index,
            secretNumber=secret_number,
            multipliedShare=multiplied_share
        )

    @retry_tx
    @transaction_method
    def alright(self, group_index, from_node_index):
        return self.contract.functions.alright(group_index, from_node_index)

    @retry_tx
    @transaction_method
    def complaint(self, group_index, from_node_index, to_node_index):
        return self.contract.functions.complaint(group_index, from_node_index,
                                                 to_node_index)

    @retry_tx
    @transaction_method
    def complaint_bad_data(self, group_index, from_node_index, to_node_index):
        return self.contract.functions.complaintBadData(group_index, from_node_index,
                                                        to_node_index)

    def is_last_dkg_successful(self, group_index):
        return self.contract.functions.isLastDKGSuccessful(group_index).call()
