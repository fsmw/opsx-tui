from __future__ import annotations

from pathlib import Path

import pytest

from opsx_tui.infrastructure.git_root_discoverer import GitRootDiscoverer


def test_no_git_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    discoverer = GitRootDiscoverer()
    assert discoverer.discover() is None


def test_git_dir_without_openspec(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(tmp_path)
    discoverer = GitRootDiscoverer()
    result = discoverer.discover()
    assert result is not None
    assert result.is_valid is False


def test_git_dir_with_openspec(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "openspec").mkdir()
    (tmp_path / "openspec" / "config.yaml").write_text("schema_version: 1\n")
    monkeypatch.chdir(tmp_path)
    discoverer = GitRootDiscoverer()
    result = discoverer.discover()
    assert result is not None
    assert result.is_valid is True
