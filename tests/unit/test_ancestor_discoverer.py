from __future__ import annotations

from pathlib import Path

from opsx_tui.domain.project import DiscoverySource
from opsx_tui.infrastructure.ancestor_discoverer import AncestorDiscoverer


def test_found_in_current_dir(tmp_path: Path) -> None:
    (tmp_path / "openspec").mkdir()
    (tmp_path / "openspec" / "config.yaml").write_text("schema_version: 1\n")
    discoverer = AncestorDiscoverer(start_dir=tmp_path)
    result = discoverer.discover()
    assert result is not None
    assert result.discovery_source == DiscoverySource.ANCESTOR_WALK
    assert result.is_valid is True
    assert result.root == tmp_path.resolve()


def test_found_in_parent_dir(tmp_path: Path) -> None:
    (tmp_path / "openspec").mkdir()
    (tmp_path / "openspec" / "config.yaml").write_text("schema_version: 1\n")
    subdir = tmp_path / "a" / "b"
    subdir.mkdir(parents=True)
    discoverer = AncestorDiscoverer(start_dir=subdir)
    result = discoverer.discover()
    assert result is not None
    assert result.root == tmp_path.resolve()


def test_not_found(tmp_path: Path) -> None:
    subdir = tmp_path / "deep" / "nested"
    subdir.mkdir(parents=True)
    discoverer = AncestorDiscoverer(start_dir=subdir, max_depth=3)
    assert discoverer.discover() is None


def test_found_incomplete_openspec(tmp_path: Path) -> None:
    (tmp_path / "openspec").mkdir()
    discoverer = AncestorDiscoverer(start_dir=tmp_path)
    result = discoverer.discover()
    assert result is not None
    assert result.is_valid is False
    assert any("config.yaml" in d.message for d in result.diagnostics)
