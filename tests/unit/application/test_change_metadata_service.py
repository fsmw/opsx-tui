from __future__ import annotations

from pathlib import Path

from opsx_tui.application.change_metadata_service import merge_metadata
from opsx_tui.domain.metadata import ChangeMetadata, Priority
from opsx_tui.domain.status import ChangeStatus
from opsx_tui.domain.workspace import (
    Change,
    WorkspaceSnapshot,
)


def _make_change(name: str, archived: bool = False) -> Change:
    return Change(
        name=name,
        change_dir=Path("/tmp"),
        absolute_change_dir=Path("/tmp"),
        artifacts=(),
        is_archived=archived,
        state=ChangeStatus.APPLYING if not archived else ChangeStatus.ARCHIVED,
    )


def _make_snapshot(
    active: tuple[Change, ...] = (),
    archived: tuple[Change, ...] = (),
) -> WorkspaceSnapshot:
    return WorkspaceSnapshot(
        root=Path("/tmp"),
        openspec_root=Path("/tmp/openspec"),
        config_yaml=True,
        specs=(),
        active_changes=active,
        archived_changes=archived,
        diagnostics=(),
        fingerprint="abc",
    )


def test_merge_active_changes() -> None:
    c1 = _make_change("change-one")
    c2 = _make_change("change-two")
    snap = _make_snapshot(active=(c1, c2))
    meta = ChangeMetadata(priority=Priority.HIGH)
    result = merge_metadata(snap, {"change-one": meta})
    assert result.active_changes[0].metadata is not None
    assert result.active_changes[0].metadata.priority == Priority.HIGH
    assert result.active_changes[1].metadata is None


def test_merge_archived_changes() -> None:
    c = _make_change("archived-change", archived=True)
    snap = _make_snapshot(archived=(c,))
    meta = ChangeMetadata(favorite=True)
    result = merge_metadata(snap, {"archived-change": meta})
    assert result.archived_changes[0].metadata is not None
    assert result.archived_changes[0].metadata.favorite is True


def test_no_match_leaves_none() -> None:
    c = _make_change("orphan")
    snap = _make_snapshot(active=(c,))
    result = merge_metadata(snap, {"other": ChangeMetadata()})
    assert result.active_changes[0].metadata is None


def test_pure_function_does_not_mutate_original() -> None:
    c = _make_change("original")
    snap = _make_snapshot(active=(c,))
    meta = ChangeMetadata(priority=Priority.URGENT)
    merge_metadata(snap, {"original": meta})
    assert snap.active_changes[0].metadata is None
