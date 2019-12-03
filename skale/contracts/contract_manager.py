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
""" SKALE Contract manager class """

from Crypto.Hash import keccak

from skale.contracts import BaseContract
from skale.utils.helper import add_0x_prefix


class ContractManager(BaseContract):
    def get_contract_address(self, name):
        contract_hash = add_0x_prefix(self.get_contract_hash_by_name(name))
        return self.contract.functions.contracts(contract_hash).call()

    def get_contract_hash_by_name(self, name):
        keccak_hash = keccak.new(data=name.encode("utf8"), digest_bits=256)
        return keccak_hash.hexdigest()
