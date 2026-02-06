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
from pydantic import AnyUrl, BaseModel, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from skale.core.constants import NESTED_DELIMITER
from skale.core.helper import _atomic_write_text
from skale.core.types import EnvType, NodeMode, NodeType
from skale.types.schain import SchainName


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


class NodeSettings(TomlBaseSettings):
    node_type: NodeType
    node_mode: NodeMode

    model_config = SettingsConfigDict(extra='forbid')


class SkaleContracts(BaseModel):
    manager: str
    ima: str


class FairContracts(BaseModel):
    fair: str


class BaseAdminSettings(TomlBaseSettings):
    env_type: EnvType
    skale_dir_host: Path
    endpoint: AnyUrl

    backup_run: bool = False
    pull_config_for_schain: str | None = None
    bite: bool = False

    tg_api_key: str | None = None
    tg_chat_id: str | None = None

    container_stop_timeout: int = 300
    max_skaled_restart_count: int = 5

    influx_url: AnyUrl | None = None

    disable_colors: bool = False

    @field_validator('skale_dir_host', mode='before')
    @classmethod
    def validate_skale_dir_host(cls, value: Path | str) -> Path:
        return Path(value).expanduser().resolve()

    @property
    def node_data_path_host(self) -> Path:
        return self.skale_dir_host / 'node_data'

    model_config = SettingsConfigDict(env_nested_delimiter=NESTED_DELIMITER)


class SkaleBaseSettings(BaseAdminSettings):
    contracts: SkaleContracts


class ActiveSettings(BaseAdminSettings):
    sgx_url: AnyUrl


class SkaleSettings(SkaleBaseSettings, ActiveSettings):
    sgx_url: AnyUrl


class SkalePassiveSettings(SkaleBaseSettings):
    schain_name: SchainName


class FairBaseSettings(BaseAdminSettings):
    contracts: FairContracts


class FairSettings(FairBaseSettings, ActiveSettings):
    sgx_url: AnyUrl


@lru_cache
def get_node_settings() -> NodeSettings:
    return NodeSettings()  # type: ignore[call-arg]


SETTINGS_MAP: dict[tuple[NodeType, NodeMode], type[BaseAdminSettings]] = {
    ('skale', 'passive'): SkalePassiveSettings,
    ('skale', 'active'): SkaleSettings,
    ('fair', 'passive'): FairBaseSettings,
    ('fair', 'active'): FairSettings,
}


def _resolve_type(node_type: NodeType, node_mode: NodeMode) -> type[BaseAdminSettings]:
    return SETTINGS_MAP.get((node_type, node_mode), BaseAdminSettings)


@overload
def get_settings() -> BaseAdminSettings: ...
@overload
def get_settings[T: BaseAdminSettings](return_type: type[T]) -> T: ...
@overload
def get_settings[T1: BaseAdminSettings, T2: BaseAdminSettings](
    return_type: tuple[type[T1], type[T2]],
) -> T1 | T2: ...


def get_settings(return_type=None):
    if return_type is not None:
        if isinstance(return_type, tuple):
            return_type = None
        else:
            return return_type()  # type: ignore[call-arg]
    node_settings = get_node_settings()
    settings_cls = _resolve_type(node_settings.node_type, node_settings.node_mode)
    return settings_cls()  # type: ignore[call-arg]


def write_node_settings_file(
    *,
    path: Path,
    node_type: NodeType,
    node_mode: NodeMode,
) -> NodeSettings:
    cfg = NodeSettings.model_validate({'node_type': node_type, 'node_mode': node_mode})
    data = cfg.model_dump(mode='json', exclude_none=True)
    _atomic_write_text(path, tomli_w.dumps(data))
    return cfg
