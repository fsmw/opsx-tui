from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from opsx_tui.application.workspace_watcher_service import WorkspaceWatcherService
from opsx_tui.domain.logging import Logger
from opsx_tui.infrastructure.watchfiles_observer import WatchfilesObserver


@pytest.fixture
def openspec_project(tmp_path: Path) -> Path:
    d = tmp_path / "openspec"
    d.mkdir(parents=True, exist_ok=True)
    (d / "config.yaml").write_text("schema_version: 1\n")
    return tmp_path


def _make_ws_service(fingerprint: str = "fp1") -> MagicMock:
    ws = MagicMock()
    ws.read_snapshot.return_value = MagicMock()
    ws.read_snapshot.return_value.fingerprint = fingerprint
    return ws


@pytest.mark.asyncio
async def test_real_watchfiles_events_trigger_callback(
    openspec_project: Path,
) -> None:
    logger = MagicMock(spec=Logger)
    observer = WatchfilesObserver(logger=logger)
    ws_service = _make_ws_service()

    service = WorkspaceWatcherService(
        observer=observer,
        logger=logger,
        workspace_service=ws_service,
    )

    events: list[object] = []
    service.start(openspec_project, lambda snap: events.append(snap))
    await asyncio.sleep(0.3)

    (openspec_project / "openspec" / "new_file.md").write_text("hello")
    await asyncio.sleep(0.6)

    assert len(events) == 1
    await service.stop()


@pytest.mark.asyncio
async def test_watch_directory_removal_stops_watcher(
    openspec_project: Path,
) -> None:
    logger = MagicMock(spec=Logger)
    observer = WatchfilesObserver(logger=logger)
    ws_service = _make_ws_service()

    service = WorkspaceWatcherService(
        observer=observer,
        logger=logger,
        workspace_service=ws_service,
    )

    service.start(openspec_project, lambda _: None)
    await asyncio.sleep(0.3)

    import shutil
    shutil.rmtree(openspec_project / "openspec")
    await asyncio.sleep(0.5)

    await service.stop()
