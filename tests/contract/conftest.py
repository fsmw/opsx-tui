from __future__ import annotations

from pathlib import Path

import pytest

from opsx_tui.application.lifecycle_service import LifecycleService
from opsx_tui.infrastructure.workspace_reader import FilesystemWorkspaceReader


@pytest.fixture
def lifecycle_service() -> LifecycleService:
    return LifecycleService()


@pytest.fixture
def reader(lifecycle_service: LifecycleService) -> FilesystemWorkspaceReader:
    return FilesystemWorkspaceReader(lifecycle_service)


@pytest.fixture
def valid_workspace() -> Path:
    return Path("tests/fixtures/workspace/minimal/openspec").resolve()
