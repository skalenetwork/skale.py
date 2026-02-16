#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2026-Present SKALE Labs
#
#   SKALE.py is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   SKALE.py is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with SKALE.py.  If not, see <https://www.gnu.org/licenses/>.

from functools import lru_cache
from pathlib import Path
from typing import overload

import tomli_w
from pydantic import AnyUrl, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from skale_core.constants import NESTED_DELIMITER
from skale_core.helper import _atomic_write_text
from skale_core.types import EnvType, NodeMode, NodeType, SchainName


class TomlBaseSettings(BaseSettings):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            TomlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


class InternalSettings(TomlBaseSettings):
    node_type: NodeType
    node_mode: NodeMode

    skale_dir_host: Path

    backup_run: bool = False
    pull_config_for_schain: str | None = None

    @field_validator('skale_dir_host', mode='before')
    @classmethod
    def validate_skale_dir_host(cls, value: Path | str) -> Path:
        return Path(value).expanduser().resolve()

    @property
    def node_data_path_host(self) -> Path:
        return self.skale_dir_host / 'node_data'

    model_config = SettingsConfigDict(extra='forbid')


class BaseNodeSettings(TomlBaseSettings):
    env_type: EnvType
    endpoint: AnyUrl

    bite: bool = False

    tg_api_key: str | None = None
    tg_chat_id: str | None = None

    container_stop_timeout: int = 300
    max_skaled_restart_count: int = 5

    influx_url: AnyUrl | None = None

    disable_colors: bool = False

    # node-cli level settings

    node_version: str
    block_device: str

    filebeat_host: str = ''
    container_configs_dir: str = ''
    skip_docker_config: bool = False
    skip_docker_cleanup: bool = False
    monitoring_containers: bool = False

    model_config = SettingsConfigDict(env_nested_delimiter=NESTED_DELIMITER)


class _SkaleBaseSettings(BaseNodeSettings):
    manager_contracts: str
    ima_contracts: str


class ActiveSettings(BaseNodeSettings):
    sgx_url: AnyUrl


class SkaleSettings(_SkaleBaseSettings, ActiveSettings):
    sgx_url: AnyUrl
    docker_lvmpy_version: str

    disable_dry_run: bool = False
    default_gas_limit: int | None = None
    default_gas_price_wei: int | None = None


class SkalePassiveSettings(_SkaleBaseSettings):
    schain_name: SchainName
    enforce_btrfs: bool = False


class FairBaseSettings(BaseNodeSettings):
    fair_contracts: str
    enforce_btrfs: bool = False


class FairSettings(FairBaseSettings, ActiveSettings):
    sgx_url: AnyUrl


@lru_cache
def get_internal_settings() -> InternalSettings:
    return InternalSettings()  # type: ignore[call-arg]


SETTINGS_MAP: dict[tuple[NodeType, NodeMode], type[BaseNodeSettings]] = {
    ('skale', 'passive'): SkalePassiveSettings,
    ('skale', 'active'): SkaleSettings,
    ('fair', 'passive'): FairBaseSettings,
    ('fair', 'active'): FairSettings,
}


def _resolve_type(node_type: NodeType, node_mode: NodeMode) -> type[BaseNodeSettings]:
    return SETTINGS_MAP.get((node_type, node_mode), BaseNodeSettings)


@overload
def get_settings() -> BaseNodeSettings: ...
@overload
def get_settings[T: BaseNodeSettings](return_type: type[T]) -> T: ...
@overload
def get_settings[T1: BaseNodeSettings, T2: BaseNodeSettings](
    return_type: tuple[type[T1], type[T2]],
) -> T1 | T2: ...


def get_settings(return_type=None):
    if return_type is not None:
        if isinstance(return_type, tuple):
            return_type = None
        else:
            return return_type()  # type: ignore[call-arg]
    node_settings = get_internal_settings()
    settings_cls = _resolve_type(node_settings.node_type, node_settings.node_mode)
    return settings_cls()  # type: ignore[call-arg]


def write_internal_settings_file(*, path: Path, data: dict) -> InternalSettings:
    cfg = InternalSettings.model_validate(data)
    dumped = cfg.model_dump(mode='json', exclude_none=True)
    _atomic_write_text(path, tomli_w.dumps(dumped))
    return cfg


def write_node_settings_file[T: BaseNodeSettings](
    *, path: Path, settings_type: type[T], data: dict
) -> T:
    cfg = settings_type.model_validate(data)
    dumped = cfg.model_dump(mode='json', exclude_none=True)
    _atomic_write_text(path, tomli_w.dumps(dumped))
    return cfg
