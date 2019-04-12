#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" SKALE base contract class """

from web3 import Web3


class BaseContract:
    def __init__(self, skale, name, address, abi):
        self.skale = skale
        self.web3 = skale.web3
        self.name = name
        self.address = Web3.toChecksumAddress(address)
        self.abi = abi
        self.contract = self.web3.eth.contract(
            address=self.address, abi=self.abi)
