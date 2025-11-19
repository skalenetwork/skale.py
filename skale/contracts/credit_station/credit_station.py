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

import logging

from eth_typing import ChecksumAddress
from web3.contract.contract import ContractEvent, ContractFunction
from web3.types import EventData, Wei

from skale.contracts.base_contract import transaction_method
from skale.contracts.skale_contract import SkaleContract
from skale.types.credit_station import PaymentReceivedEvent
from skale.types.schain import SchainName
from skale.utils.helper import schain_name_to_hash

logger = logging.getLogger(__name__)


def get_events_in_chunks(
    event: ContractEvent,
    from_block: int,
    to_block: int | None = None,
    chunk_size: int = 10000,
    **filter_args,
) -> list[EventData]:
    if to_block is None:
        to_block = event.w3.eth.block_number

    events = []
    current_block = from_block
    logger.info(f'Fetching events: {from_block} - {to_block}, chunk_size: {chunk_size}')
    while current_block <= to_block:
        logger.info(
            f'Fetching chunk: {current_block} - {min(current_block + chunk_size - 1, to_block)}'
        )
        end_block = min(current_block + chunk_size - 1, to_block)
        chunk_events = event.get_logs(
            from_block=current_block, to_block=end_block, argument_filters=filter_args
        )
        events.extend(chunk_events)
        current_block = end_block + 1
    return events


class CreditStation(SkaleContract):
    @transaction_method
    def buy(
        self, schain_name: SchainName, purchaser: ChecksumAddress, token: ChecksumAddress
    ) -> ContractFunction:
        return self.contract.functions.buy(schain_name, purchaser, token)

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

    def get_payment_received_events(
        self,
        from_block: int = 0,
        to_block: int | None = None,
        chunk_size: int = 50000,
        schain_name: SchainName | None = None,
    ) -> list[PaymentReceivedEvent]:
        filter_args = {}
        if schain_name is not None:
            schain_hash = schain_name_to_hash(schain_name)
            filter_args['schainHash'] = schain_hash

        events = get_events_in_chunks(
            self.contract.events.PaymentReceived, from_block, to_block, chunk_size, **filter_args
        )

        return [
            PaymentReceivedEvent(
                payment_id=event['args']['id'],
                schain_hash=event['args']['schainHash'],
                from_address=event['args']['from'],
                to_address=event['args']['to'],
                token_address=event['args']['tokenAddress'],
                block_number=event['blockNumber'],
            )
            for event in events
        ]
