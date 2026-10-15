# skale.py-core

Core settings and types for SKALE node. Lightweight — no web3 or sgx dependencies.

## Installation

```bash
pip install skale.py-core
```

## Usage

### Types

```python
from skale_core.types import EnvType, NodeType, NodeMode, SchainName

node_type: NodeType = 'skale'
node_mode: NodeMode = 'active'
env: EnvType = 'mainnet'
name: SchainName = SchainName('my-chain')
```

### Writing settings files

```python
from pathlib import Path
from skale_core.settings import write_internal_settings_file, write_node_settings_file, SkaleSettings

write_internal_settings_file(
    path=Path('/etc/skale/node.toml'),
    data={'node_type': 'skale', 'node_mode': 'active', 'skale_dir_host': '/etc/skale'},
)

write_node_settings_file(
    path=Path('/etc/skale/settings.toml'),
    settings_type=SkaleSettings,
    data={
        'env_type': 'mainnet',
        'endpoint': 'http://localhost:8545',
        'node_version': '1.0.0',
        'block_device': '/dev/sda',
        'manager_contracts': '0x1',
        'ima_contracts': '0x2',
        'sgx_url': 'https://sgx.example.com',
        'docker_lvmpy_version': '1.0.0',
    },
)
```

### Reading settings at runtime

```python
from skale_core.settings import get_settings, SkaleSettings

settings = get_settings(SkaleSettings)
print(settings.endpoint, settings.env_type)
```
