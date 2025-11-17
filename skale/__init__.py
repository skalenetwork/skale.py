import sys

if sys.version_info < (3, 11):
    raise EnvironmentError('Python 3.11 or above is required')

from skale.fair_manager import FairManager
from skale.mainnet_credit_station import MainnetCreditStation
from skale.mainnet_ima import MainnetIma
from skale.mainnet_ima import MainnetIma as SkaleIma  # todo: deprecated, to be removed in v8
from skale.schain_credit_station import SchainCreditStation
from skale.schain_ima import SchainIma
from skale.skale_allocator import SkaleAllocator
from skale.skale_manager import SkaleManager

__all__ = [
    'SkaleManager',
    'SkaleAllocator',
    'SkaleIma',
    'MainnetIma',
    'FairManager',
    'SchainIma',
    'MainnetCreditStation',
    'SchainCreditStation',
]
