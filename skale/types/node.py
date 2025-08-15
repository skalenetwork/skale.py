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

import socket
from dataclasses import dataclass
from enum import IntEnum
from typing import List, NewType, TypedDict, TypeVar

from eth_typing import BlockNumber, ChecksumAddress, HexStr
from eth_utils.address import to_checksum_address

from skale.types.schain import SchainStructureWithStatus
from skale.types.validator import ValidatorId
from skale.utils.constants import ZERO_ADDRESS

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


FairNodeType = TypeVar('FairNodeType', bound='FairNode')


@dataclass
class FairNode:
    id: NodeId
    ip: bytes
    ip_str: str
    domain_name: str
    address: ChecksumAddress
    port: Port
    name: str

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'ip_str': self.ip_str,
            'domain_name': self.domain_name,
            'address': self.address,
            'port': self.port,
            'name': self.name,
        }


FairNodeForChainConfigType = TypeVar('FairNodeForChainConfigType', bound='FairNodeForChainConfig')


@dataclass
class FairNodeForChainConfig(FairNode):
    reward_wallet_address: ChecksumAddress
    public_key: HexStr

    def to_dict(self) -> dict:
        return {
            'reward_wallet_address': self.reward_wallet_address,
            'public_key': self.public_key,
            **super().to_dict(),
        }


def get_ghost_fair_node(node_id: NodeId) -> FairNode:
    ip_str = '255.255.255.255'
    return FairNode(
        id=node_id,
        ip=socket.inet_aton(ip_str),
        ip_str=ip_str,
        domain_name='',
        address=to_checksum_address(ZERO_ADDRESS),
        port=Port(10000),
        name='',
    )


class NodeWithId(Node):
    id: NodeId


class NodeWithSchains(NodeWithId):
    schains: List[SchainStructureWithStatus]
