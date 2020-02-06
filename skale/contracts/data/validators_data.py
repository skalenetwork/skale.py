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
""" Get SKALE validator data """
from web3 import Web3
from skale.contracts import BaseContract


class ValidatorsData(BaseContract):
    def get_reward_period(self):
        constants = self.skale.get_contract_by_name('constants')
        return constants.contract.functions.rewardPeriod().call()

    def get_delta_period(self):
        constants = self.skale.get_contract_by_name('constants')
        return constants.contract.functions.deltaPeriod().call()

    def get_validated_array(self, node_id):
        node_id_bytes = Web3.solidityKeccak(['uint256'], [node_id])
        return self.contract.functions.getValidatedArray(node_id_bytes).call()