from __future__ import annotations

from pathlib import Path

import pytest

from opsx_tui.domain.change_parser import ChangeState
from opsx_tui.domain.workspace import Change
from opsx_tui.infrastructure.workspace_reader import FilesystemWorkspaceReader


@pytest.fixture
def reader() -> FilesystemWorkspaceReader:
    return FilesystemWorkspaceReader()


class TestChangeBackwardCompat:
    def test_construct_without_new_fields(self) -> None:
        change = Change(
            name="old",
            change_dir=Path("/tmp/old"),
            absolute_change_dir=Path("/tmp/old").resolve(),
            artifacts=(),
            is_archived=False,
        )
        assert change.state == ChangeState.UNKNOWN
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
            state=ChangeState.ACTIVE,
        )
        assert change.state == ChangeState.ACTIVE


class TestWorkspaceReaderIntegration:
    def test_valid_change_parsed(self, reader: FilesystemWorkspaceReader) -> None:
        root = Path("tests/fixtures/workspace/minimal/openspec").resolve()
        snap = reader.read_workspace(root)
        active = [c for c in snap.active_changes if c.state != ChangeState.UNKNOWN]
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
                assert c.state == ChangeState.ACTIVE
                return
        pytest.fail("active-change not found")

    def test_archived_change_state(
        self, reader: FilesystemWorkspaceReader,
    ) -> None:
        root = Path("tests/fixtures/workspace/minimal/openspec").resolve()
        snap = reader.read_workspace(root)
        for c in snap.archived_changes:
            assert c.state == ChangeState.ARCHIVED
