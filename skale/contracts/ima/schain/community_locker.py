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

from eth_typing import ChecksumAddress
from web3.contract.contract import ContractFunction

from skale.contracts.base_contract import transaction_method
from skale.contracts.skale_contract import SkaleContract
from skale.types.schain import SchainName
from skale.utils.helper import schain_name_to_hash


class CommunityLocker(SkaleContract):
    """ "Community locker"""

    @transaction_method
    def set_time_limit_per_message(
        self, schain_name: SchainName, new_time_limit: int
    ) -> ContractFunction:
        """Set time limit"""
        return self.contract.functions.setTimeLimitPerMessage(schain_name, new_time_limit)

    def constant_setter_role(self) -> bytes:
        return self.contract.functions.CONSTANT_SETTER_ROLE().call()

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return self.contract.functions.hasRole(role, address).call()

    @transaction_method
    def revoke_role(self, role: bytes, address: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.revokeRole(role, address)

    @transaction_method
    def grant_role(self, role: bytes, address: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.grantRole(role, address)

    def check_allow_to_send_msg(self, schain_name: SchainName, address: ChecksumAddress) -> int:
        return self.contract.functions.checkAllowedToSendMessage(
            schain_name_to_hash(schain_name), address
        ).call()

    def schain_name_to_hash(self) -> bytes:
        return self.contract.functions.schainHash().call()

    def mainnet_hash(self) -> bytes:
        return self.contract.functions.MAINNET_HASH().call()

    def is_active_user(self, address) -> bool:
        return self.contract.functions.activeUsers(address).call()

    def last_message_timestamp(self, address) -> int:
        return self.contract.functions.lastMessageTimeStamp(address).call()

    def time_limit_per_msg(self, schain_name: SchainName) -> int:
        return self.contract.functions.timeLimitPerMessage(schain_name_to_hash(schain_name)).call()
