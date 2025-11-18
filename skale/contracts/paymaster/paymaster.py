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


class Paymaster(SkaleContract):
    """Paymaster contract"""

    @transaction_method
    def add_schain(self, schain_name: SchainName) -> ContractFunction:
        return self.contract.functions.addSchain(schain_name)

    @transaction_method
    def remove_schain(self, schain_name: SchainName) -> ContractFunction:
        return self.contract.functions.removeSchain(schain_name_to_hash(schain_name))

    @transaction_method
    def add_validator(
        self, validator_id: int, validator_address: ChecksumAddress
    ) -> ContractFunction:
        return self.contract.functions.addValidator(validator_id, validator_address)

    @transaction_method
    def remove_validator(self, validator_id: int) -> ContractFunction:
        return self.contract.functions.removeValidator(validator_id)

    @transaction_method
    def set_validator_address(
        self, validator_id: int, new_address: ChecksumAddress
    ) -> ContractFunction:
        return self.contract.functions.setValidatorAddress(validator_id, new_address)

    @transaction_method
    def set_active_nodes(self, validator_id: int, nodes_amount: int) -> ContractFunction:
        return self.contract.functions.setActiveNodes(validator_id, nodes_amount)

    @transaction_method
    def set_max_replenishment_period(self, month: int) -> ContractFunction:
        return self.contract.functions.setMaxReplenishmentPeriod(month)

    @transaction_method
    def set_schain_price(self, price: int) -> ContractFunction:
        return self.contract.functions.setSchainPrice(price)

    @transaction_method
    def set_skl_price(self, price: int) -> ContractFunction:
        return self.contract.functions.setSklPrice(price)

    @transaction_method
    def set_allowed_skl_price_lag(self, lag_seconds: int) -> ContractFunction:
        return self.contract.functions.setAllowedSklPriceLag(lag_seconds)

    @transaction_method
    def set_skale_token(self, token_address: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.setSkaleToken(token_address)

    @transaction_method
    def clear_history(self, timestamp_before: int) -> ContractFunction:
        return self.contract.functions.clearHistory(timestamp_before)

    @transaction_method
    def pay(self, schain_name: SchainName, month: int) -> ContractFunction:
        return self.contract.functions.pay(schain_name_to_hash(schain_name), month)

    @transaction_method
    def claim(self, to_address: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.claim(to_address)

    @transaction_method
    def set_version(self, new_version) -> ContractFunction:
        return self.contract.functions.setVersion(new_version)

    def get_schain_expiration_timestamp(self, schain_name: SchainName) -> ContractFunction:
        return self.contract.functions.getSchainExpirationTimestamp(
            schain_name_to_hash(schain_name)
        ).call()

    def get_reward_amount(self, validator_id: int) -> int:
        return self.contract.functions.getRewardAmount(validator_id).call()

    def get_nodes_number(self, validator_id: int) -> int:
        return self.contract.functions.getNodesNumber(validator_id).call()

    def get_historical_active_nodes_number(self, validator_id: int, time_when: int) -> int:
        return self.contract.functions.getHistoricalActiveNodesNumber(
            validator_id, time_when
        ).call()

    def get_historical_total_active_nodes_number(self, time_when: int) -> int:
        return self.contract.functions.getHistoricalTotalActiveNodesNumber(time_when).call()

    def get_validator_number(self) -> int:
        return self.contract.functions.getValidatorsNumber().call()

    def get_schain_names(self) -> str:
        return self.contract.functions.getSchainsNames().call()

    def get_total_reward(self, time_from: int, time_to: int) -> int:
        return self.contract.functions.getTotalReward(time_from, time_to).call()

    @transaction_method
    def set_nodes_amount(self, validator_id: int, amount: int) -> ContractFunction:
        return self.contract.functions.setNodesAmount(validator_id, amount)

    @transaction_method
    def claim_for(self, validator_id: int, address: ChecksumAddress) -> ContractFunction:
        return self.contract.functions.claimFor(validator_id, address)

    def get_schain_number(self) -> str:
        return self.contract.functions.getSchainsNumber().call()

    def get_schain(self, schain_name: SchainName) -> list:
        return self.contract.functions.schains(schain_name_to_hash(schain_name)).call()

    def get_max_replenishment_period(self) -> int:
        return self.contract.functions.maxReplenishmentPeriod().call()

    def get_schain_price_per_month(self) -> int:
        return self.contract.functions.schainPricePerMonth().call()

    def get_one_skl_price(self) -> int:
        return self.contract.functions.oneSklPrice().call()

    def get_skl_price_timestamp(self) -> int:
        return self.contract.functions.sklPriceTimestamp().call()

    def get_allowed_skl_price_lag(self) -> int:
        return self.contract.functions.allowedSklPriceLag().call()

    def get_skale_token(self) -> int:
        return self.contract.functions.skaleToken().call()

    @transaction_method
    def skip_time(self, seconds: int) -> ContractFunction:
        return self.contract.functions.skipTime(seconds)

    def get_effective_timestamp(self) -> int:
        return self.contract.functions.effectiveTimestamp().call()

    def get_debts_amount(self, debt_id: int) -> int:
        return self.contract.functions.debts(debt_id).call()

    def get_debts_begin(self) -> int:
        return self.contract.functions.debtsBegin().call()

    def get_debts_end(self) -> int:
        return self.contract.functions.debtsEnd().call()
