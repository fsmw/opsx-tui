from __future__ import annotations

from pathlib import Path

from opsx_tui.domain.project import DiagnosticLevel, DiscoverySource
from opsx_tui.infrastructure.validation import validate_project


def test_nonexistent_path() -> None:
    assert validate_project(Path("/nonexistent"), DiscoverySource.CLI_ARG) is None


def test_missing_openspec_dir(tmp_path: Path) -> None:
    result = validate_project(tmp_path, DiscoverySource.CLI_ARG)
    assert result is not None
    assert result.is_valid is False
    assert any(d.level == DiagnosticLevel.ERROR for d in result.diagnostics)


def test_missing_config_yaml(tmp_path: Path) -> None:
    (tmp_path / "openspec").mkdir()
    result = validate_project(tmp_path, DiscoverySource.CLI_ARG)
    assert result is not None
    assert result.is_valid is False
    assert any("config.yaml" in d.message for d in result.diagnostics)


def test_valid_project(tmp_path: Path) -> None:
    (tmp_path / "openspec").mkdir()
    (tmp_path / "openspec" / "config.yaml").write_text("schema_version: 1\n")
    result = validate_project(tmp_path, DiscoverySource.CLI_ARG)
    assert result is not None
    assert result.is_valid is True
    assert result.discovery_source == DiscoverySource.CLI_ARG
