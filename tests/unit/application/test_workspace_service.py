from __future__ import annotations

from pathlib import Path

from opsx_tui.application.workspace_service import WorkspaceService
from opsx_tui.domain.ports import WorkspaceReader
from opsx_tui.domain.project import Diagnostic
from opsx_tui.domain.workspace import WorkspaceSnapshot


class FakeWorkspaceReader(WorkspaceReader):
    def __init__(self, snapshot: WorkspaceSnapshot) -> None:
        self._snapshot = snapshot
        self.last_root: Path | None = None

    def read_workspace(self, openspec_root: Path) -> WorkspaceSnapshot:
        self.last_root = openspec_root
        return self._snapshot


def _make_snapshot(root: Path = Path("/fake")) -> WorkspaceSnapshot:
    return WorkspaceSnapshot(
        root=root,
        openspec_root=root / "openspec",
        config_yaml=True,
        specs=(),
        active_changes=(),
        archived_changes=(),
        diagnostics=(),
        fingerprint="fake-fp",
    )


def test_read_snapshot_delegates_to_reader() -> None:
    snapshot = _make_snapshot()
    reader = FakeWorkspaceReader(snapshot)
    service = WorkspaceService(reader)
    result = service.read_snapshot(Path("/test-root"))
    assert result is snapshot
    assert reader.last_root == Path("/test-root")


def test_read_snapshot_with_empty_workspace() -> None:
    snapshot = _make_snapshot()
    reader = FakeWorkspaceReader(snapshot)
    service = WorkspaceService(reader)
    result = service.read_snapshot(Path("/empty"))
    assert len(result.specs) == 0
    assert len(result.active_changes) == 0


def test_read_snapshot_passes_through_diagnostics() -> None:
    diag = Diagnostic(level="warning", message="test diag")
    snapshot = WorkspaceSnapshot(
        root=Path("/fake"),
        openspec_root=Path("/fake/openspec"),
        config_yaml=True,
        specs=(),
        active_changes=(),
        archived_changes=(),
        diagnostics=(diag,),
        fingerprint="fp",
    )
    reader = FakeWorkspaceReader(snapshot)
    service = WorkspaceService(reader)
    result = service.read_snapshot(Path("/test"))
    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].message == "test diag"
