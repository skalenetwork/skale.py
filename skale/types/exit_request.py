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

from dataclasses import dataclass

from eth_typing import ChecksumAddress

from skale.types.node import NodeId


@dataclass
class ExitRequest:
    request_id: int
    user: ChecksumAddress
    node_id: NodeId
    amount: int
    unlock_date: int

    def to_dict(self) -> dict:
        return {
            'request_id': self.request_id,
            'user': self.user,
            'node_id': self.node_id,
            'amount': self.amount,
            'unlock_date': self.unlock_date,
        }


def exit_request_from_tuple(data: tuple) -> ExitRequest:
    return ExitRequest(
        request_id=data[0],
        user=data[1],
        node_id=data[2],
        amount=data[3],
        unlock_date=data[4],
    )
