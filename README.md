# skale.py

[![PyPI version](https://badge.fury.io/py/skale.py.svg)](https://badge.fury.io/py/skale.py)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/skalenetwork/skale.py/Test)
[![codecov](https://codecov.io/gh/skalenetwork/skale.py/branch/develop/graph/badge.svg?token=XHiZ15ijpa)](https://codecov.io/gh/skalenetwork/skale.py)
![Libraries.io dependency status for GitHub repo](https://img.shields.io/librariesio/github/skalenetwork/skale.py)
[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

Python client library used in SKALE network components.

* Python 3.11+ support
* Compatibility with `web3.py` v7

### Installation

```bash
pip install skale.py
```

### Usage

#### Supported wallets

* Ledger Wallet (works with Ledger Nano S and other models)
* RPC Wallet (works with [SKALE Transactions Manager](https://github.com/skalenetwork/transactions-manager))
* SGX Wallet (works with [SKALE SGX Wallet](https://github.com/skalenetwork/sgxwallet))
* Web3 Wallet (works with `web3.py` embeded functions)

#### Library initialization

With embeded Web3Wallet

```python
from skale import SkaleManager
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3

web3 = init_web3(ENDPOINT)
wallet = Web3Wallet(private_key, web3)
skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)
```

With external transactions manager:

```python
from skale import SkaleManager
from skale.wallets import RPCWallet

web3 = init_web3(ENDPOINT)
wallet = RPCWallet(TM_URL)
skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)
```

Interactions with SKALE contracts

```python
active_nodes = skale.nodes.get_active_node_ips()
schains = skale.schains.get_schains_for_owner('0x...')
```

#### Working in multiple threads

Due to the web3.py v5 limitations you have to create separate instances of the skale.py for the each thread.\
Take a look on the `tests/multithreading_test.py` for the reference.

#### Code samples

You can find usage examples [here](https://github.com/skalenetwork/skale.py-examples).

### Development

##### Add pre-commit hook:

```bash
nano .git/hooks/pre-commit
```

```
ruff check .
```

##### Install local version (with hot reload)

```bash
virtualenv venv
. venv/bin/activate 
pip install -e .[dev]
```

#### Build and publish library

```bash
bash build_and_publish.sh major/minor/patch
```

#### If you're using .env file

```bash
 export $(cat .env | xargs) && bash build_and_publish.sh major/minor/patch
```

#### Versioning

The version scheme for this repo is `{major}.{minor}.{patch}`
For more details see: <https://semver.org/>

#### Testing

Run local ganache and deploy SKALE Manager:

```bash
MANAGER_TAG=... ETH_PRIVATE_KEY=... bash scripts/deploy_manager.sh
```

Running full test suite:

```bash
bash scripts/run_tests.sh
```

Running test suite manually:

See `tests/README.md`

### License

![GitHub](https://img.shields.io/github/license/skalenetwork/skale.py.svg)

All contributions are made under the [GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html). See [LICENSE](LICENSE).
