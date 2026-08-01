from __future__ import annotations

from pathlib import Path

import pytest

from opsx_tui.application.lifecycle_service import LifecycleService
from opsx_tui.domain.status import ChangeStatus
from opsx_tui.domain.workspace import Change
from opsx_tui.infrastructure.workspace_reader import FilesystemWorkspaceReader


@pytest.fixture
def lifecycle_service() -> LifecycleService:
    return LifecycleService()


@pytest.fixture
def reader(lifecycle_service: LifecycleService) -> FilesystemWorkspaceReader:
    return FilesystemWorkspaceReader(lifecycle_service)


class TestChangeBackwardCompat:
    def test_construct_without_new_fields(self) -> None:
        change = Change(
            name="old",
            change_dir=Path("/tmp/old"),
            absolute_change_dir=Path("/tmp/old").resolve(),
            artifacts=(),
            is_archived=False,
        )
        assert change.state == ChangeStatus.UNKNOWN
        assert change.parsed_proposal is None
        assert change.parsed_design is None
        assert change.parsed_tasks is None
        assert change.artifact_diagnostics == ()

    def test_construct_with_new_fields(self) -> None:
        change = Change(
            name="new",
            change_dir=Path("/tmp/new"),
            absolute_change_dir=Path("/tmp/new").resolve(),
            artifacts=(),
            is_archived=False,
            state=ChangeStatus.PLANNING,
        )
        assert change.state == ChangeStatus.PLANNING


class TestWorkspaceReaderIntegration:
    def test_valid_change_parsed(self, reader: FilesystemWorkspaceReader) -> None:
        root = Path("tests/fixtures/workspace/minimal/openspec").resolve()
        snap = reader.read_workspace(root)
        active = [c for c in snap.active_changes if c.state != ChangeStatus.UNKNOWN]
        assert len(active) >= 1

    def test_valid_change_has_parsed_content(
        self, reader: FilesystemWorkspaceReader,
    ) -> None:
        root = Path("tests/fixtures/workspace/minimal/openspec").resolve()
        snap = reader.read_workspace(root)
        for c in snap.active_changes:
            if c.name == "active-change":
                assert c.parsed_proposal is not None
                assert c.parsed_design is not None
                assert c.parsed_tasks is not None
                return
        pytest.fail("active-change not found")

    def test_valid_change_good_state(
        self, reader: FilesystemWorkspaceReader,
    ) -> None:
        root = Path("tests/fixtures/workspace/minimal/openspec").resolve()
        snap = reader.read_workspace(root)
        for c in snap.active_changes:
            if c.name == "active-change":
                assert c.state == ChangeStatus.READY
                return
        pytest.fail("active-change not found")

    def test_archived_change_state(
        self, reader: FilesystemWorkspaceReader,
    ) -> None:
        root = Path("tests/fixtures/workspace/minimal/openspec").resolve()
        snap = reader.read_workspace(root)
        for c in snap.archived_changes:
            assert c.state == ChangeStatus.ARCHIVED
