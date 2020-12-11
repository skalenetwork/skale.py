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
""" NodeRotation.sol functions """

import functools
from skale.contracts.base_contract import BaseContract


class NodeRotation(BaseContract):
    """Wrapper for NodeRotation.sol functions"""

    @property
    @functools.lru_cache()
    def schains(self):
        return self.skale.schains

    def get_rotation(self, schain_name):
        schain_id = self.schains.name_to_id(schain_name)
        rotation_data = self.contract.functions.getRotation(schain_id).call()
        return {
            'leaving_node': rotation_data[0],
            'new_node': rotation_data[1],
            'finish_ts': rotation_data[2],
            'rotation_id': rotation_data[3]
        }

    def get_leaving_history(self, node_id):
        raw_history = self.contract.functions.getLeavingHistory(node_id).call()
        history = [
            {
                'id': schain[0],
                'finished_rotation': schain[1]
            }
            for schain in raw_history
        ]
        return history

    def is_rotation_in_progress(self, schain_name):
        schain_id = self.schains.name_to_id(schain_name)
        return self.contract.functions.isRotationInProgress(schain_id).call()

    def wait_for_new_node(self, schain_name):
        schain_id = self.schains.name_to_id(schain_name)
        return self.contract.functions.waitForNewNode(schain_id).call()
