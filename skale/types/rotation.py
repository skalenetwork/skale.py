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

from collections import namedtuple
from dataclasses import dataclass
from typing import TypedDict

from skale.types.node import NodeId
from skale.types.schain import SchainHash


RotationNodeData = namedtuple('RotationNodeData', ['index', 'node_id', 'public_key'])


class NodesSwap(TypedDict):
    leaving_node_id: NodeId
    new_node_id: NodeId


class BlsPublicKey(TypedDict):
    blsPublicKey0: str
    blsPublicKey1: str
    blsPublicKey2: str
    blsPublicKey3: str


class NodesGroup(TypedDict):
    rotation: NodesSwap | None
    nodes: dict[NodeId, RotationNodeData]
    finish_ts: int | None
    bls_public_key: BlsPublicKey | None


@dataclass
class Rotation:
    leaving_node_id: NodeId
    new_node_id: NodeId
    freeze_until: int
    rotation_counter: int


class RotationSwap(TypedDict):
    schain_id: SchainHash
    finished_rotation: int
