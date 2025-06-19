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
from typing import Any, Callable, Tuple, TypedDict

from eth_typing import ChecksumAddress
from web3.contract.contract import ContractFunction
from web3.types import Wei

from skale.contracts.base_contract import transaction_method
from skale.contracts.skale_manager_contract import SkaleManagerContract
from skale.types.validator import ValidatorId


class EarnedData(TypedDict):
    earned: Wei
    end_month: int


def formatter(method: Callable[..., Tuple[Wei, int]]) -> Callable[..., EarnedData]:
    @wraps(method)
    def wrapper(self: SkaleManagerContract, *args: Any, **kwargs: Any) -> EarnedData:
        res = method(self, *args, **kwargs)
        return EarnedData(
            {
                'earned': res[0],
                'end_month': res[1],
            }
        )

    return wrapper


class Distributor(SkaleManagerContract):
    """Wrapper for Distributor.sol functions"""

    @formatter
    def get_earned_bounty_amount(
        self, validator_id: ValidatorId, address: ChecksumAddress
    ) -> Tuple[Wei, int]:
        """Get earned bounty amount for the validator

        :param validator_id: ID of the validator
        :type validator_id: int
        :returns: Earned bounty amount and end month
        :rtype: dict
        """
        return tuple(
            self.contract.functions.getAndUpdateEarnedBountyAmount(validator_id).call(
                {'from': address}
            )
        )

    @formatter
    def get_earned_fee_amount(self, address: ChecksumAddress) -> Tuple[Wei, int]:
        """Get earned fee amount for the address

        :param address: Address of the validator
        :type address: ChecksumAddress
        :returns: Earned bounty amount and end month
        :rtype: dict
        """
        return tuple(self.contract.functions.getEarnedFeeAmount().call({'from': address}))

    @transaction_method
    def withdraw_bounty(self, validator_id: ValidatorId, to: ChecksumAddress) -> 'ContractFunction':
        """Withdraw earned bounty to specified address

        :param validator_id: ID of the validator
        :type validator_id: int
        :param to: Address to transfer bounty
        :type to: str
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.withdrawBounty(validator_id, to)

    @transaction_method
    def withdraw_fee(self, to: ChecksumAddress) -> 'ContractFunction':
        """Withdraw earned fee to specified address

        :param to: Address to transfer bounty
        :type to: str
        :returns: Transaction results
        :rtype: TxRes
        """
        return self.contract.functions.withdrawFee(to)
