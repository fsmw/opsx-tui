from __future__ import annotations

from pathlib import Path

from opsx_tui.domain.project import Diagnostic, DiagnosticLevel
from opsx_tui.domain.workspace import (
    ArtifactInfo,
    ArtifactKind,
    CanonicalSpec,
    Change,
    WorkspaceSnapshot,
)


def test_artifact_kind_values() -> None:
    assert ArtifactKind.PROPOSAL.value == "proposal"
    assert ArtifactKind.DESIGN.value == "design"
    assert ArtifactKind.TASKS.value == "tasks"
    assert ArtifactKind.SPECS.value == "specs"


def test_artifact_info_frozen() -> None:
    info = ArtifactInfo(
        kind=ArtifactKind.PROPOSAL,
        path=Path("proposal.md"),
        absolute_path=Path("/root/proposal.md"),
        exists=True,
    )
    assert info.kind == ArtifactKind.PROPOSAL
    assert info.path == Path("proposal.md")
    assert info.exists


def test_canonical_spec_with_spec_file() -> None:
    spec = CanonicalSpec(
        name="my-capability",
        spec_dir=Path("specs/my-capability"),
        spec_file=Path("specs/my-capability/spec.md"),
        absolute_spec_dir=Path("/root/specs/my-capability"),
        absolute_spec_file=Path("/root/specs/my-capability/spec.md"),
    )
    assert spec.name == "my-capability"
    assert spec.spec_file is not None


def test_canonical_spec_without_spec_file() -> None:
    spec = CanonicalSpec(
        name="empty-dir",
        spec_dir=Path("specs/empty-dir"),
        spec_file=None,
        absolute_spec_dir=Path("/root/specs/empty-dir"),
        absolute_spec_file=None,
    )
    assert spec.spec_file is None
    assert spec.absolute_spec_file is None


def test_change_active() -> None:
    change = Change(
        name="my-change",
        change_dir=Path("changes/my-change"),
        absolute_change_dir=Path("/root/changes/my-change"),
        artifacts=(),
        is_archived=False,
    )
    assert not change.is_archived


def test_change_archived() -> None:
    change = Change(
        name="my-change",
        change_dir=Path("changes/archive/my-change"),
        absolute_change_dir=Path("/root/changes/archive/my-change"),
        artifacts=(),
        is_archived=True,
    )
    assert change.is_archived


def test_workspace_snapshot_frozen() -> None:
    snap = WorkspaceSnapshot(
        root=Path("/root"),
        openspec_root=Path("/root/openspec"),
        config_yaml=True,
        specs=(),
        active_changes=(),
        archived_changes=(),
        diagnostics=(),
        fingerprint="abc",
    )
    assert snap.root == Path("/root")
    assert snap.config_yaml
    assert snap.fingerprint == "abc"


def test_workspace_snapshot_with_diagnostics() -> None:
    diag = Diagnostic(level=DiagnosticLevel.WARNING, message="missing spec.md")
    snap = WorkspaceSnapshot(
        root=Path("/root"),
        openspec_root=Path("/root/openspec"),
        config_yaml=True,
        specs=(),
        active_changes=(),
        archived_changes=(),
        diagnostics=(diag,),
        fingerprint="def",
    )
    assert len(snap.diagnostics) == 1
    assert snap.diagnostics[0].message == "missing spec.md"
