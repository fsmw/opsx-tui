from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from opsx_tui.infrastructure.recent_projects_discoverer import (
    RecentProjectsDiscoverer,
    write_recent_project,
)


def _make_override(
    json_path: Path,
) -> Callable[[], Path]:
    def _override() -> Path:
        return json_path
    return _override


def test_no_file(monkeypatch: pytest.MonkeyPatch) -> None:
    json_path = Path("/nonexistent/recent-projects.json")
    monkeypatch.setattr(
        "opsx_tui.infrastructure.recent_projects_discoverer._recent_projects_path",
        _make_override(json_path),
    )
    assert RecentProjectsDiscoverer().discover() is None


def test_empty_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    json_path = tmp_path / "recent-projects.json"
    json_path.write_text("{}")
    monkeypatch.setattr(
        "opsx_tui.infrastructure.recent_projects_discoverer._recent_projects_path",
        _make_override(json_path),
    )
    assert RecentProjectsDiscoverer().discover() is None


def test_stale_entry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    json_path = tmp_path / "recent-projects.json"
    json_path.write_text(json.dumps({"recent_projects": [{"path": "/does/not/exist"}]}))
    monkeypatch.setattr(
        "opsx_tui.infrastructure.recent_projects_discoverer._recent_projects_path",
        _make_override(json_path),
    )
    assert RecentProjectsDiscoverer().discover() is None


def test_valid_entry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project_dir = tmp_path / "project"
    (project_dir / "openspec").mkdir(parents=True)
    (project_dir / "openspec" / "config.yaml").write_text("schema_version: 1\n")
    json_path = tmp_path / "recent-projects.json"
    json_path.write_text(json.dumps({"recent_projects": [{"path": str(project_dir)}]}))
    monkeypatch.setattr(
        "opsx_tui.infrastructure.recent_projects_discoverer._recent_projects_path",
        _make_override(json_path),
    )
    result = RecentProjectsDiscoverer().discover()
    assert result is not None
    assert result.is_valid is True


def test_write_recent_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project_dir = tmp_path / "project"
    (project_dir / "openspec").mkdir(parents=True)
    (project_dir / "openspec" / "config.yaml").write_text("schema_version: 1\n")
    json_path = tmp_path / "recent-projects.json"
    monkeypatch.setattr(
        "opsx_tui.infrastructure.recent_projects_discoverer._recent_projects_path",
        _make_override(json_path),
    )
    write_recent_project(project_dir)
    assert json_path.exists()
    data = json.loads(json_path.read_text())
    assert len(data["recent_projects"]) == 1
    assert data["recent_projects"][0]["path"] == str(project_dir.resolve())


def test_write_dedup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project_dir = tmp_path / "project"
    (project_dir / "openspec").mkdir(parents=True)
    (project_dir / "openspec" / "config.yaml").write_text("schema_version: 1\n")
    json_path = tmp_path / "recent-projects.json"
    monkeypatch.setattr(
        "opsx_tui.infrastructure.recent_projects_discoverer._recent_projects_path",
        _make_override(json_path),
    )
    write_recent_project(project_dir)
    write_recent_project(project_dir)
    data = json.loads(json_path.read_text())
    assert len(data["recent_projects"]) == 1


def test_write_cap(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    json_path = tmp_path / "recent-projects.json"
    monkeypatch.setattr(
        "opsx_tui.infrastructure.recent_projects_discoverer._recent_projects_path",
        _make_override(json_path),
    )
    for i in range(15):
        d = tmp_path / f"project{i}"
        d.mkdir()
        write_recent_project(d)
    data = json.loads(json_path.read_text())
    assert len(data["recent_projects"]) == 10
