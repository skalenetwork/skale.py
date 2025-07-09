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

from __future__ import annotations

from dataclasses import dataclass
from typing import List, NewType, TypedDict

from skale.types.dkg import DkgId, G2Point
from skale.types.node import MirageNode, NodeId

CommitteeIndex = NewType('CommitteeIndex', int)
Timestamp = NewType('Timestamp', int)


@dataclass
class Committee:
    node_ids: List[NodeId]
    dkg_id: DkgId
    common_public_key: G2Point
    starting_timestamp: Timestamp


CommitteeGroup = TypedDict(
    'CommitteeGroup',
    {
        'ts': Timestamp,
        'index': CommitteeIndex,
        'group': List[MirageNode],
        'committee': Committee,
    },
)
