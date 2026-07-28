from __future__ import annotations

import os
import tomllib
from pathlib import Path

import platformdirs  # noqa: I001

from opsx_tui.domain.config import Config
from opsx_tui.domain.errors import ConfigLoadError
from opsx_tui.domain.ports import ConfigLoader

_DEFAULT_CONFIG = Config()

_OPSX_PREFIX = "OPSX_TUI_"
_SECTION_SEP = "__"


class TomlConfigLoader(ConfigLoader):
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root

    def load(self) -> Config:
        layers: list[dict] = [
            _DEFAULT_CONFIG.model_dump(),
        ]

        global_path = self._global_config_path()
        if global_path.exists():
            layers.append(self._load_toml(global_path))

        project_path = self._project_config_path()
        if project_path is not None and project_path.exists():
            layers.append(self._load_toml(project_path))

        env_dict = self._load_env()
        if env_dict:
            layers.append(env_dict)

        merged: dict = {}
        for layer in layers:
            self._deep_merge(merged, layer)

        return Config.model_validate(merged)

    @staticmethod
    def _global_config_path() -> Path:
        return (
            Path(platformdirs.user_config_dir("opsx-tui", ensure_exists=False))
            / "config.toml"
        )

    def _project_config_path(self) -> Path | None:
        root = self._project_root
        if root is None:
            return None
        return root / ".opsx-tui" / "config.toml"

    @staticmethod
    def _load_toml(path: Path) -> dict:
        try:
            with path.open("rb") as f:
                raw = tomllib.load(f)
            return raw
        except (tomllib.TOMLDecodeError, OSError) as e:
            raise ConfigLoadError(path, e) from e

    @staticmethod
    def _load_env() -> dict:
        result: dict = {}
        for key, value in os.environ.items():
            if not key.startswith(_OPSX_PREFIX):
                continue
            inner_key = key[len(_OPSX_PREFIX) :]
            parts = inner_key.lower().split(_SECTION_SEP)
            current = result
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            current[parts[-1]] = value
        return result

    @staticmethod
    def _deep_merge(target: dict, source: dict) -> None:
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                TomlConfigLoader._deep_merge(target[key], value)
            else:
                target[key] = value
