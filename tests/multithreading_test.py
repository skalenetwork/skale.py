#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" SKALE test multithreading """

import threading

from skale import Skale
import skale.utils.helper as Helper
from skale.utils.web3_utils import init_web3
from tests.constants import ENDPOINT, TEST_ABI_FILEPATH, DEFAULT_NODE_NAME


def get_node_data():
    skale = Skale(ENDPOINT, TEST_ABI_FILEPATH)
    for _ in range(0, 30):
        skale.nodes_data.get_by_name(DEFAULT_NODE_NAME)

def test_multithead_calls():
    init_web3(ENDPOINT)
    monitors = []
    for _ in range(0, 5):
        monitor = threading.Thread(target=get_node_data, daemon=True)
        monitor.start()
        monitors.append(monitor)
        print('!!!')
    for monitor in monitors:
        monitor.join()