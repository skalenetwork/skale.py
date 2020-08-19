#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2020-Present SKALE Labs
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


class KeyStorage(BaseContract):
    def get_bls_public_key(self, group_index, node_index):
        return self.contract.functions.getBLSPublicKey(group_index, node_index).call()

    def get_broadcasted_data(self, group_index, node_index):
        return self.contract.functions.getBroadcastedData(group_index, node_index).call()

    def get_common_public_key(self, group_index):
        return self.contract.functions.getCommonPublicKey(group_index).call()

    def get_previous_public_key(self, group_index):
        return self.contract.functions.getPreviousPublicKey(group_index).call()

    def get_all_previous_public_keys(self, group_index):
        return self.contract.functions.getAllPreviousPublicKeys(group_index).call()
