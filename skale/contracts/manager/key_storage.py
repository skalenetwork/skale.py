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

from typing import List
from skale.types.dkg import G2Point
from skale.contracts.skale_manager_contract import SkaleManagerContract
from skale.types.schain import SchainHash


class KeyStorage(SkaleManagerContract):
    def get_common_public_key(self, schain_hash: SchainHash) -> G2Point:
        return G2Point(*self.contract.functions.getCommonPublicKey(schain_hash).call())

    def get_previous_public_key(self, schain_hash: SchainHash) -> G2Point:
        return G2Point(*self.contract.functions.getPreviousPublicKey(schain_hash).call())

    def get_all_previous_public_keys(self, schain_hash: SchainHash) -> List[G2Point]:
        return [
            G2Point(*key)
            for key in self.contract.functions.getAllPreviousPublicKeys(schain_hash).call()
        ]
