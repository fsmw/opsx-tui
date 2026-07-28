from __future__ import annotations

from pathlib import Path

import pytest

from opsx_tui.domain.project import DiagnosticLevel
from opsx_tui.infrastructure.workspace_reader import FilesystemWorkspaceReader


@pytest.fixture
def reader() -> FilesystemWorkspaceReader:
    return FilesystemWorkspaceReader()


def test_reads_minimal_workspace(reader: FilesystemWorkspaceReader) -> None:
    root = Path("tests/fixtures/workspace/minimal/openspec").resolve()
    snap = reader.read_workspace(root)
    assert snap.config_yaml
    assert len(snap.specs) == 1
    assert snap.specs[0].name == "first-capability"
    assert len(snap.active_changes) == 1
    assert len(snap.archived_changes) == 1
    assert snap.active_changes[0].name == "active-change"
    assert not snap.active_changes[0].is_archived
    assert snap.archived_changes[0].is_archived
    assert len(snap.fingerprint) > 0


def test_active_change_artifacts(reader: FilesystemWorkspaceReader) -> None:
    root = Path("tests/fixtures/workspace/minimal/openspec").resolve()
    snap = reader.read_workspace(root)
    change = snap.active_changes[0]
    artifacts = {a.kind.value for a in change.artifacts}
    assert "proposal" in artifacts
    assert "design" in artifacts
    assert "tasks" in artifacts


def test_fingerprint_determinism(
    reader: FilesystemWorkspaceReader, tmp_path: Path
) -> None:
    src = Path("tests/fixtures/workspace/minimal/openspec").resolve()
    dst = tmp_path / "copy"
    _copytree(src, dst)
    snap1 = reader.read_workspace(dst)
    snap2 = reader.read_workspace(dst)
    assert snap1.fingerprint == snap2.fingerprint


def test_incomplete_workspace(reader: FilesystemWorkspaceReader) -> None:
    root = Path("tests/fixtures/workspace/incomplete/openspec").resolve()
    snap = reader.read_workspace(root)
    warnings = [d for d in snap.diagnostics if d.level == DiagnosticLevel.WARNING]
    assert len(warnings) > 0
    assert snap.config_yaml
    assert len(snap.specs) == 0
    assert len(snap.active_changes) == 1


def test_empty_workspace(reader: FilesystemWorkspaceReader) -> None:
    root = Path("tests/fixtures/workspace/empty/openspec").resolve()
    snap = reader.read_workspace(root)
    assert snap.config_yaml
    assert len(snap.specs) == 0
    assert len(snap.active_changes) == 0
    assert len(snap.archived_changes) == 0


def test_unknown_files_ignored(
    reader: FilesystemWorkspaceReader, tmp_path: Path
) -> None:
    openspec = tmp_path / "openspec"
    openspec.mkdir(parents=True)
    (openspec / "config.yaml").write_text("schema_version: 1")
    (openspec / "random_file.txt").write_text("who cares")
    weird_dir = openspec / "random_dir"
    weird_dir.mkdir()
    (weird_dir / "nested.txt").write_text("nope")
    snap = reader.read_workspace(openspec)
    assert snap.config_yaml
    errors = [d for d in snap.diagnostics if d.level == DiagnosticLevel.ERROR]
    assert len(errors) == 0


def test_nonexistent_path(reader: FilesystemWorkspaceReader) -> None:
    from opsx_tui.domain.errors import WorkspaceReadError

    with pytest.raises(WorkspaceReadError):
        reader.read_workspace(Path("/nonexistent-openspec-root"))


def _copytree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        s = item
        d = dst / item.name
        if s.is_dir():
            _copytree(s, d)
        else:
            d.write_bytes(s.read_bytes())
            d.touch()
