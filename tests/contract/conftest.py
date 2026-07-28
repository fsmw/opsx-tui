from __future__ import annotations

from pathlib import Path

import pytest

from opsx_tui.infrastructure.workspace_reader import FilesystemWorkspaceReader


@pytest.fixture
def reader() -> FilesystemWorkspaceReader:
    return FilesystemWorkspaceReader()


@pytest.fixture
def valid_workspace() -> Path:
    return Path("tests/fixtures/workspace/minimal/openspec").resolve()
