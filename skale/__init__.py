# flake8: noqa: E402

import sys

if sys.version_info < (3, 7):
    raise EnvironmentError("Python 3.7 or above is required")

from skale.skale_manager import SkaleManager
from skale.skale_manager import SkaleManager as Skale  # todo: deprecated naming, will be removed in skale.py v5

from skale.skale_allocator import SkaleAllocator
from skale.skale_ima import SkaleIma
