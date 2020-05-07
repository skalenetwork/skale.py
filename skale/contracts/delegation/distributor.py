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

from functools import wraps

from skale.contracts import BaseContract, transaction_method
from skale.dataclasses.tx_res import TxRes
from skale.utils.constants import GAS


def formatter(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        res = method(self, *args, **kwargs)
        return {
            'earned': res[0],
            'end_month': res[1],
        }
    return wrapper


class Distributor(BaseContract):
    """Wrapper for Distributor.sol functions"""

    @formatter
    def get_earned_bounty_amount(self, validator_id: int) -> dict:
        """Get earned bounty amount for the validator

        :param validator_id: ID of the validator
        :type validator_id: int
        :returns: Earned bounty amount and end month
        :rtype: dict
        """
        return self.contract.functions.getAndUpdateEarnedBountyAmount(validator_id).call()

    @formatter
    def get_earned_fee_amount(self, address: str) -> dict:
        """Get earned fee amount for the address

        :param address: Address of the validator
        :type address: str
        :returns: Earned bounty amount and end month
        :rtype: dict
        """
        return self.contract.functions.getEarnedFeeAmount().call({
            'from': address
        })

    @transaction_method(gas_limit=GAS['withdraw_bounty'])
    def withdraw_bounty(self, validator_id: int, to: str) -> TxRes:
        """Withdraw earned bounty to specified address

        :param validator_id: ID of the validator
        :type validator_id: int
        :param to: Address to transfer bounty
        :type to: str
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.withdrawBounty(validator_id, to)

    @transaction_method(gas_limit=GAS['withdraw_fee'])
    def withdraw_fee(self, to: str) -> TxRes:
        """Withdraw earned fee to specified address

        :param to: Address to transfer bounty
        :type to: str
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.withdrawFee(to)
