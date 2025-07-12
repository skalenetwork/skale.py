#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2024-Present SKALE Labs
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

from enum import IntEnum
from dataclasses import dataclass
from typing import List, NewType, TypedDict

from eth_typing import BlockNumber, ChecksumAddress, HexStr

from skale.types.schain import SchainStructureWithStatus
from skale.types.validator import ValidatorId


NodeId = NewType('NodeId', int)
Port = NewType('Port', int)


class NodeStatus(IntEnum):
    ACTIVE = 0
    LEAVING = 1
    LEFT = 2
    IN_MAINTENANCE = 3


class Node(TypedDict):
    name: str
    ip: bytes
    publicIP: bytes
    port: Port
    start_block: BlockNumber
    last_reward_date: int
    finish_time: int
    status: NodeStatus
    validator_id: ValidatorId
    publicKey: HexStr
    domain_name: str


@dataclass
class MirageNode:
    id: NodeId
    ip: bytes
    ip_str: str
    domain_name: str
    address: ChecksumAddress
    port: Port
    name: str
    public_key: HexStr

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'ip_str': self.ip_str,
            'domain_name': self.domain_name,
            'address': self.address,
            'port': self.port,
            'name': self.name,
            'public_key': self.public_key,
        }


class NodeWithId(Node):
    id: NodeId


class NodeWithSchains(NodeWithId):
    schains: List[SchainStructureWithStatus]
