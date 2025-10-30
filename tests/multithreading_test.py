"""SKALE test multithreading"""

import threading

from skale import SkaleManager
from skale.utils.helper import get_skale_manager_address
from skale.utils.web3_utils import init_web3
from tests.constants import DEFAULT_NODE_NAME, ENDPOINT, TEST_ABI_FILEPATH


def get_node_data():
    skale = SkaleManager(ENDPOINT, get_skale_manager_address(TEST_ABI_FILEPATH))
    for _ in range(0, 30):
        skale.nodes.get_by_name(DEFAULT_NODE_NAME)


def test_multithread_calls():
    init_web3(ENDPOINT)
    monitors = []
    for _ in range(0, 5):
        monitor = threading.Thread(target=get_node_data, daemon=True)
        monitor.start()
        monitors.append(monitor)
    for monitor in monitors:
        monitor.join()
