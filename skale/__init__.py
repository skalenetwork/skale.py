# flake8: noqa: E402

import sys

if sys.version_info < (3, 6):
    raise EnvironmentError("Python 3.6 or above is required")

from skale.manager.skale_manager import SkaleManager
from skale.manager.skale_manager import SkaleManager as Skale

