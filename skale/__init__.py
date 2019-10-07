# flake8: noqa: E402

import sys

if sys.version_info < (3, 5):
    raise EnvironmentError("Python 3.5 or above is required")

from skale.main import Skale
from skale.contracts import (Manager, Token, Nodes, SChains,
                             Validators, Groups, BaseContract, Constants)
