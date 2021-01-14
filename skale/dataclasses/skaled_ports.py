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

from enum import Enum


class SkaledPorts(Enum):
    PROPOSAL = 0
    CATCHUP = 1
    WS_JSON = 2
    HTTP_JSON = 3
    BINARY_CONSENSUS = 4
    ZMQ_BROADCAST = 5
    MTA = 6
    WSS_JSON = 7
    HTTPS_JSON = 8
    INFO_HTTP_JSON = 9
