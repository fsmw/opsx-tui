from __future__ import annotations

import os
from pathlib import Path

from opsx_tui.domain.project import DiscoverySource
from opsx_tui.infrastructure.env_var_discoverer import EnvVarDiscoverer


def test_env_var_not_set() -> None:
    os.environ.pop("OPSX_TUI_PROJECT", None)
    discoverer = EnvVarDiscoverer()
    assert discoverer.discover() is None


def test_env_var_set_to_nonexistent_path() -> None:
    os.environ["OPSX_TUI_PROJECT"] = "/nonexistent/path"
    discoverer = EnvVarDiscoverer()
    assert discoverer.discover() is None


def test_env_var_set_to_valid_path(tmp_path: Path) -> None:
    project_dir = tmp_path / "myproject"
    (project_dir / "openspec").mkdir(parents=True)
    (project_dir / "openspec" / "config.yaml").write_text("schema_version: 1\n")
    os.environ["OPSX_TUI_PROJECT"] = str(project_dir)
    discoverer = EnvVarDiscoverer()
    result = discoverer.discover()
    assert result is not None
    assert result.discovery_source == DiscoverySource.ENV_VAR
    assert result.is_valid is True
    assert result.root.resolve() == project_dir.resolve()
