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

import os

ENV = os.getenv('ENV', 'prod')
ALLOWED_TS_DIFF = int(os.getenv('ALLOWED_TS_DIFF') or 300)
DISABLE_DRY_RUN = os.getenv('DISABLE_DRY_RUN', 'False') == 'True'
DEFAULT_GAS_LIMIT = int(os.getenv('DEFAULT_GAS_LIMIT') or 10 ** 7)
DEFAULT_GAS_PRICE_WEI = int(os.getenv('DEFAULT_GAS_PRICE_WEI') or 0)
LAST_BLOCK_FILE = os.getenv('LAST_BLOCK_FILE')
