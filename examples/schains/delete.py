import sys

from skale import BlockchainEnv, Skale
from skale.utils.account_tools import init_wallet
import skale.utils.helper as Helper

skale = Skale(BlockchainEnv.DO)
wallet = init_wallet()

if __name__ == "__main__":
    schain_name = sys.argv[1]

    res = skale.manager.delete_schain(schain_name, wallet)
    receipt = Helper.await_receipt(skale.web3, res['tx'])
    Helper.check_receipt(receipt)
    print(f'sChain {schain_name} removed!')
