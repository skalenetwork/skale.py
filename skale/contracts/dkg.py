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

from skale.contracts import BaseContract
from skale.transactions.tools import post_transaction
from skale.utils.constants import GAS


class DKG(BaseContract):
    def broadcast(self, group_index, node_index,
                  verification_vector, secret_key_conribution):
        op = self.contract.functions.broadcast(group_index, node_index,
                                               verification_vector,
                                               secret_key_conribution)
        return post_transaction(self.skale.wallet, op, GAS['dkg_broadcast'])

    def response(self, group_index, from_node_index,
                 secret_number, multiplied_share):
        op = self.contract.functions.response(group_index, from_node_index,
                                              secret_number,
                                              multiplied_share)
        return post_transaction(self.skale.wallet, op, GAS['dkg_response'])

    def allright(self, group_index, from_node_index):
        op = self.contract.functions.allright(group_index, from_node_index)
        return post_transaction(self.skale.wallet, op, GAS['dkg_allright'])

    def complaint(self, group_index, from_node_index, to_node_index):
        op = self.contract.functions.complaint(group_index, from_node_index,
                                               to_node_index)
        return post_transaction(self.skale.wallet, op, GAS['dkg_complaint'])
