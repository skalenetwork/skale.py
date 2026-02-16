import tomllib
from pathlib import Path

import pytest
from pydantic import ValidationError
from skale_core.settings import (
    BaseNodeSettings,
    FairBaseSettings,
    FairSettings,
    SkalePassiveSettings,
    SkaleSettings,
    _resolve_type,
    write_internal_settings_file,
    write_node_settings_file,
)
from skale_core.types import NodeMode, NodeType

BASE_NODE_DATA = {
    'env_type': 'mainnet',
    'endpoint': 'http://localhost:8545',
    'node_version': '1.0.0',
    'block_device': '/dev/sda',
}

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


def test_write_internal_settings(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    node_type_mode: tuple[NodeType, NodeMode],
) -> None:
    node_type, node_mode = node_type_mode
    monkeypatch.setenv('SKALE_DIR_HOST', str(tmp_path))
    path = tmp_path / 'node.toml'
    data = {'node_type': node_type, 'node_mode': node_mode, 'skale_dir_host': str(tmp_path)}
    result = write_internal_settings_file(path=path, data=data)
    assert result.node_type == node_type
    assert result.node_mode == node_mode
    with open(path, 'rb') as f:
        data = tomllib.load(f)
    assert data['node_type'] == node_type
    assert data['node_mode'] == node_mode


def test_write_internal_settings_invalid_type(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv('SKALE_DIR_HOST', str(tmp_path))
    with pytest.raises(ValidationError):
        write_internal_settings_file(
            path=tmp_path / 'node.toml',
            data={'node_type': 'unknown', 'node_mode': 'active', 'skale_dir_host': str(tmp_path)},
        )


@pytest.fixture(
    params=[
        (
            SkaleSettings,
            {
                **BASE_NODE_DATA,
                'manager_contracts': '0x1',
                'ima_contracts': '0x2',
                'sgx_url': SGX_URL,
                'docker_lvmpy_version': '1.0.0',
            },
        ),
        (
            SkalePassiveSettings,
            {
                **BASE_NODE_DATA,
                'manager_contracts': '0x1',
                'ima_contracts': '0x2',
                'schain_name': 'test-chain',
            },
        ),
        (FairBaseSettings, {**BASE_NODE_DATA, 'fair_contracts': '0x3'}),
        (
            FairSettings,
            {**BASE_NODE_DATA, 'fair_contracts': '0x3', 'sgx_url': SGX_URL},
        ),
    ]
)
def node_settings_entry(
    request: pytest.FixtureRequest,
) -> tuple[type[BaseNodeSettings], dict]:
    return request.param


def test_write_node_settings(
    tmp_path: Path, node_settings_entry: tuple[type[BaseNodeSettings], dict]
) -> None:
    settings_type, data = node_settings_entry
    path = tmp_path / 'settings.toml'
    result = write_node_settings_file(path=path, settings_type=settings_type, data=data)
    assert isinstance(result, settings_type)
    assert str(result.endpoint) == data['endpoint'] + '/'
    assert path.exists()
    with open(path, 'rb') as f:
        written = tomllib.load(f)
    assert written['env_type'] == data['env_type']


def test_node_settings_rejects_missing_fields(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        write_node_settings_file(
            path=tmp_path / 'settings.toml',
            settings_type=SkaleSettings,
            data={'env_type': 'mainnet'},
        )


def test_resolve_type() -> None:
    assert _resolve_type('skale', 'active') is SkaleSettings
    assert _resolve_type('skale', 'passive') is SkalePassiveSettings
    assert _resolve_type('fair', 'active') is FairSettings
    assert _resolve_type('fair', 'passive') is FairBaseSettings
    assert _resolve_type('skale', 'unknown') is BaseNodeSettings
