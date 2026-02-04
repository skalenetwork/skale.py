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

from pathlib import Path

import tomli_w
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from skale.core.helper import _atomic_write_text
from skale.core.types import NodeMode, NodeType


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
