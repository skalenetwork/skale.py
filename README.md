# skale.py

[![PyPI version](https://badge.fury.io/py/skale.py.svg)](https://badge.fury.io/py/skale.py)
[![Build Status](https://travis-ci.com/skalenetwork/skale.py.svg?token=tLesVRTSHvWZxoyqXdoA&branch=develop)](https://travis-ci.com/skalenetwork/skale.py) 
[![codecov](https://codecov.io/gh/skalenetwork/skale.py/branch/develop/graph/badge.svg?token=XHiZ15ijpa)](https://codecov.io/gh/skalenetwork/skale.py)
[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

Python client library used in SKALE network components.

-   Python 3.6+ support

### Installation

```bash
pip install skale
```

### Usage

Library initialization

```python
from skale import Skale
skale = Skale('RPC_ENDPOINT', 'JSON_ABI_FILEPATH')
```

Interactions with SKALE contracts

```python
active_nodes = skale.nodes_data.get_active_node_ips()
schains = skale.schains_data.get_schains_for_owner('0x...')
```

#### Working in multiple threads

Due to the web3.py v5 limitations you have to create separate instances of the skale.py for the each thread.  
Take a look on the `tests/multithreading_test.py` for the reference.

### Development

##### Install local version (with hot reload)

    virtualenv venv
    . venv/bin/activate 
    pip install -e .[dev]

#### Build and publish library

```bash
bash build_and_publish.sh major/minor/patch
```

#### If you're using .env file

```bash
 export $(cat .env | xargs) && bash build_and_publish.sh major/minor/patch
```

##### Format your code before commit

Show flake8 errors on file change:

```sh
# Test flake8
WHEN_CHANGED_EVENT=file_modified when-changed -v -s -r -1 skale/ tests/ examples/ -c "clear; flake8 web3 tests ens && echo 'flake8 success' || echo 'error'"
```

Install `when-changed`:

```bash
 pip install https://github.com/joh/when-changed/archive/master.zip
```

#### Versioning

The version scheme for this repo is `{major}.{minor}.{patch}`
For more details see: <https://semver.org/>

#### Testing

For running full test suite you will need `skale-manager` repo cloned alongside with `skale-py` directory

Running full test suite:

```bash
bash test_runner.sh
```

Running test suite manually:

See `tests/README.md`

### License

![GitHub](https://img.shields.io/github/license/skalenetwork/skale.py.svg)

All contributions are made under the [GNU Lesser General Public License v3](https://www.gnu.org/licenses/lgpl-3.0.en.html). See [LICENSE](LICENSE).
