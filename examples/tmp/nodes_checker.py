import skale.utils.helper as Helper
from skale.utils.helper import ip_from_bytes
from skale import Skale
from skale.utils.account_tools import init_wallet

from examples.helper import ENDPOINT, ABI_FILEPATH

Helper.init_default_logger()


wallet = init_wallet()
skale = Skale(ENDPOINT, ABI_FILEPATH)


for _ in range(0, 1000000):
    nodes_ips = skale.nodes_data.get_active_node_ips()
    ips = []
    for ip in nodes_ips:
        ips.append(ip_from_bytes(ip))

    print('====')
    print('IPS', ips)
    print('====')
