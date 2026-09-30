#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2025-Present SKALE Labs
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
from web3.types import BlockIdentifier, Wei

from skale.contracts.base_contract import transaction_method
from skale.contracts.skale_contract import SkaleContract
from skale.types.credit_station import PaymentId, PaymentInfo
from skale.types.schain import SchainName


class CreditStation(SkaleContract):
    @transaction_method
    def buy(
        self,
        schain_name: SchainName,
        purchaser: ChecksumAddress,
        token: ChecksumAddress,
        value: Wei,
    ) -> ContractFunction:
        return self.contract.functions.buy(schain_name, purchaser, token, value)

    @transaction_method
    def set_price(self, token: ChecksumAddress, price: Wei) -> ContractFunction:
        return self.contract.functions.setPrice(token, price)

    def get_price(self, token: ChecksumAddress) -> Wei:
        return self.contract.functions.getPrice(token).call()

    def get_prices(self) -> dict[ChecksumAddress, Wei]:
        tokens = self.get_supported_tokens()
        return {token: self.get_price(token) for token in tokens}

    def get_supported_tokens(self) -> list[ChecksumAddress]:
        return self.contract.functions.getSupportedTokens().call()

    def is_token_accepted(self, token: ChecksumAddress) -> bool:
        return self.contract.functions.isTokenAccepted(token).call()

    def get_last_payment_id(self, block_identifier: BlockIdentifier) -> PaymentId:
        return self.contract.functions.getLastPaymentId().call(block_identifier=block_identifier)

    def get_payment_info(self, payment_id: PaymentId) -> PaymentInfo | None:
        info = PaymentInfo(*self.contract.functions.paymentsInfo(payment_id).call())
        return info if info.block_number else None
