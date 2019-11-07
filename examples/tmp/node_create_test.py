import os
import threading

import skale.utils.helper as Helper
from skale import Skale
from skale.utils.account_tools import init_wallet
from skale.utils.constants import LONG_LINE
from tests.utils import generate_random_node_data

from examples.helper import ENDPOINT, ABI_FILEPATH


Helper.init_default_logger()

TM_URL = os.environ['TM_URL']
wallet = init_wallet()
skale = Skale(ENDPOINT, ABI_FILEPATH, transactions_manager_url=TM_URL)
# skale = Skale(ENDPOINT, ABI_FILEPATH)

amount = 1000


def create_node(skale, wallet):
    ip, public_ip, port, name = generate_random_node_data()
    port = 10000
    skale.manager.create_node(ip, port, name, wallet, public_ip)


def create_nodes():
    skale = Skale(ENDPOINT, ABI_FILEPATH, transactions_manager_url=TM_URL)
    print(f'Creating {amount} nodes...')
    for i in range(int(amount)):
        print(LONG_LINE)
        print(f'Creating {i+1}/{amount} node...')
        create_node(skale, wallet)


monitors = []
for _ in range(0, 5):
    monitor = threading.Thread(target=create_nodes, daemon=True)
    monitor.start()
    monitors.append(monitor)
for monitor in monitors:
    monitor.join()
