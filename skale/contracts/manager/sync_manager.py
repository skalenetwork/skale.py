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
""" Schains.sol functions """

from __future__ import annotations

import socket
from collections import namedtuple
from typing import List

from skale.contracts.base_contract import BaseContract, transaction_method
from skale.transactions.result import TxRes


class IpRange(namedtuple('IpRange', ['start_ip', 'end_ip'])):
    @classmethod
    def from_packed(cls, packed_ips: List[bytes]) -> IpRange:
        return cls(
            socket.inet_ntoa(packed_ips[0]),
            socket.inet_ntoa(packed_ips[1])
        )


class SyncManager(BaseContract):
    """Wrapper for SyncManager.sol functions"""

    @transaction_method
    def add_ip_range(self, name, start_ip: bytes, end_ip: bytes) -> TxRes:
        return self.contract.functions.addIPRange(
            name,
            socket.inet_aton(start_ip),
            socket.inet_aton(end_ip)
        )

    @transaction_method
    def remove_ip_range(self, name: str) -> TxRes:
        return self.contract.functions.removeIPRange(name)

    def get_ip_ranges_number(self) -> int:
        return self.contract.functions.getIPRangesNumber().call()

    def get_ip_range_by_index(self, index: int) -> IpRange:
        packed = self.contract.functions.getIPRangeByIndex(index).call()
        return IpRange.from_packed(packed)

    def get_ip_range_by_name(self, name: str) -> tuple:
        packed = self.contract.functions.getIPRangeByName(name).call()
        return IpRange.from_packed(packed)

    def grant_sync_manager_role(self, address: str) -> TxRes:
        return self.grant_role(self.sync_manager_role(), address)

    def sync_manager_role(self) -> bytes:
        return self.contract.functions.SYNC_MANAGER_ROLE().call()

    @ transaction_method
    def grant_role(self, role: bytes, owner: str) -> TxRes:
        return self.contract.functions.grantRole(role, owner)
