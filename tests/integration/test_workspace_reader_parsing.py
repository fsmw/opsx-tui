from __future__ import annotations

from pathlib import Path

import pytest

from opsx_tui.infrastructure.workspace_reader import FilesystemWorkspaceReader


@pytest.fixture
def reader() -> FilesystemWorkspaceReader:
    return FilesystemWorkspaceReader()


def test_workspace_reader_parses_specs(reader: FilesystemWorkspaceReader) -> None:
    root = Path("tests/fixtures/workspace/minimal/openspec").resolve()
    snap = reader.read_workspace(root)
    for spec in snap.specs:
        assert spec.raw_markdown is not None
        assert spec.parsed is not None
        assert spec.parsed.name == spec.name
        assert spec.parsed.raw_markdown == spec.raw_markdown


def test_delta_specs_parsed_via_workspace_reader(
    reader: FilesystemWorkspaceReader,
) -> None:
    openspec = Path("tests/fixtures/spec-parsing/delta").resolve()
    snap = reader.read_workspace(openspec)
    for change in snap.active_changes:
        for delta in change.delta_specs:
            assert delta.raw_markdown is not None
            assert delta.parsed is not None
            assert len(delta.parsed.requirements) > 0


def test_spec_with_spec_file_none(reader: FilesystemWorkspaceReader) -> None:
    openspec = Path("tests/fixtures/workspace/empty/openspec").resolve()
    snap = reader.read_workspace(openspec)
    for spec in snap.specs:
        assert spec.parsed is None
