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
from typing import List, NamedTuple, NewType, Tuple

from eth_typing import HexStr
from enum import Enum

from skale.types.node import NodeId


Fp2Point = namedtuple('Fp2Point', ['a', 'b'])
DkgId = NewType('DkgId', int)


class G2Point(NamedTuple):
    x: Fp2Point
    y: Fp2Point


VerificationVector = NewType('VerificationVector', List[G2Point])


class KeyShare(NamedTuple):
    publicKey: Tuple[bytes | HexStr, bytes | HexStr]
    share: bytes | HexStr


class Status(Enum):
    SUCCESS = 0
    BROADCAST = 1
    ALRIGHT = 2
    FAILED = 3


class Round(NamedTuple):
    id: DkgId
    status: Status
    nodes: List[NodeId]
    publicKey: G2Point
    startingBlockNumber: int
    numberOfBroadcasted: int
    hashedData: List[bytes]
    numberOfCompleted: int
    completed: List[bool]
