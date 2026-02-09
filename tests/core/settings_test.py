import tomllib
from pathlib import Path

import pytest
from pydantic import ValidationError

from skale.core.settings import (
    BaseAdminSettings,
    FairBaseSettings,
    FairSettings,
    SkalePassiveSettings,
    SkaleSettings,
    _resolve_type,
    write_admin_settings_file,
    write_node_settings_file,
)
from skale.core.types import NodeMode, NodeType

BASE_ADMIN_DATA = {
    'env_type': 'mainnet',
    'skale_dir_host': '/tmp/skale',
    'endpoint': 'http://localhost:8545',
}

SKALE_CONTRACTS = {'manager': '0x1', 'ima': '0x2'}
FAIR_CONTRACTS = {'fair': '0x3'}
SGX_URL = 'https://sgx.example.com'


@pytest.fixture(
    params=[
        ('skale', 'active'),
        ('skale', 'passive'),
        ('fair', 'active'),
        ('fair', 'passive'),
    ]
)
def node_type_mode(request: pytest.FixtureRequest) -> tuple[NodeType, NodeMode]:
    return request.param


def test_write_node_settings(tmp_path: Path, node_type_mode: tuple[NodeType, NodeMode]) -> None:
    node_type, node_mode = node_type_mode
    path = tmp_path / 'node.toml'
    result = write_node_settings_file(path=path, node_type=node_type, node_mode=node_mode)
    assert result.node_type == node_type
    assert result.node_mode == node_mode
    with open(path, 'rb') as f:
        data = tomllib.load(f)
    assert data == {'node_type': node_type, 'node_mode': node_mode}


def test_write_node_settings_invalid_type(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        write_node_settings_file(
            path=tmp_path / 'node.toml', node_type='unknown', node_mode='active'
        )


@pytest.fixture(
    params=[
        (SkaleSettings, {**BASE_ADMIN_DATA, 'contracts': SKALE_CONTRACTS, 'sgx_url': SGX_URL}),
        (
            SkalePassiveSettings,
            {**BASE_ADMIN_DATA, 'contracts': SKALE_CONTRACTS, 'schain_name': 'test-chain'},
        ),
        (FairBaseSettings, {**BASE_ADMIN_DATA, 'contracts': FAIR_CONTRACTS}),
        (FairSettings, {**BASE_ADMIN_DATA, 'contracts': FAIR_CONTRACTS, 'sgx_url': SGX_URL}),
    ]
)
def admin_settings_entry(
    request: pytest.FixtureRequest,
) -> tuple[type[BaseAdminSettings], dict]:
    return request.param


def test_write_admin_settings(
    tmp_path: Path, admin_settings_entry: tuple[type[BaseAdminSettings], dict]
) -> None:
    settings_type, data = admin_settings_entry
    path = tmp_path / 'admin.toml'
    result = write_admin_settings_file(path=path, settings_type=settings_type, data=data)
    assert isinstance(result, settings_type)
    assert str(result.endpoint) == data['endpoint'] + '/'
    assert path.exists()
    with open(path, 'rb') as f:
        written = tomllib.load(f)
    assert written['env_type'] == data['env_type']


def test_admin_settings_rejects_missing_fields(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        write_admin_settings_file(
            path=tmp_path / 'admin.toml',
            settings_type=SkaleSettings,
            data={'env_type': 'mainnet'},
        )


def test_resolve_type() -> None:
    assert _resolve_type('skale', 'active') is SkaleSettings
    assert _resolve_type('skale', 'passive') is SkalePassiveSettings
    assert _resolve_type('fair', 'active') is FairSettings
    assert _resolve_type('fair', 'passive') is FairBaseSettings
    assert _resolve_type('skale', 'unknown') is BaseAdminSettings
