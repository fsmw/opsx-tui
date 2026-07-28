from __future__ import annotations

from pathlib import Path

import pytest

from opsx_tui.domain.errors import WorkspaceReadError
from opsx_tui.domain.ports import WorkspaceReader
from opsx_tui.domain.workspace import WorkspaceSnapshot


def _check_snapshot_invariants(snapshot: WorkspaceSnapshot) -> None:
    assert isinstance(snapshot.root, Path)
    assert isinstance(snapshot.openspec_root, Path)
    assert isinstance(snapshot.config_yaml, bool)
    assert isinstance(snapshot.specs, tuple)
    assert isinstance(snapshot.active_changes, tuple)
    assert isinstance(snapshot.archived_changes, tuple)
    assert isinstance(snapshot.diagnostics, tuple)
    assert isinstance(snapshot.fingerprint, str)

    for spec in snapshot.specs:
        assert isinstance(spec.name, str)
        assert isinstance(spec.spec_dir, Path)

    for change in snapshot.active_changes:
        assert isinstance(change.name, str)
        assert isinstance(change.artifacts, tuple)

    for change in snapshot.archived_changes:
        assert isinstance(change.artifacts, tuple)

    for diag in snapshot.diagnostics:
        assert isinstance(diag.message, str)


def test_workspace_reader_contract(
    reader: WorkspaceReader, valid_workspace: Path
) -> None:
    snapshot = reader.read_workspace(valid_workspace)
    _check_snapshot_invariants(snapshot)
    assert snapshot.config_yaml
    assert len(snapshot.specs) >= 1
    assert len(snapshot.active_changes) >= 1
    assert len(snapshot.archived_changes) >= 1


def test_workspace_reader_rejects_nonexistent(reader: WorkspaceReader) -> None:
    with pytest.raises(WorkspaceReadError):
        reader.read_workspace(Path("/nonexistent/path"))


def test_workspace_reader_rejects_file(reader: WorkspaceReader, tmp_path: Path) -> None:
    f = tmp_path / "not_a_dir"
    f.write_text("")
    with pytest.raises(WorkspaceReadError):
        reader.read_workspace(f)
