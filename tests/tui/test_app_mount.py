from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from opsx_tui.application.container import Container
from opsx_tui.domain.project import DiscoverySource, Project
from opsx_tui.domain.workspace import WorkspaceSnapshot


def _make_valid_project(root: Path) -> Project:
    return Project(
        root=root,
        openspec_root=root / "openspec",
        discovery_source=DiscoverySource.ANCESTOR_WALK,
        is_valid=True,
    )


def _make_snapshot(root: Path) -> WorkspaceSnapshot:
    return WorkspaceSnapshot(
        root=root,
        openspec_root=root / "openspec",
        config_yaml=True,
        specs=(),
        active_changes=(),
        archived_changes=(),
        diagnostics=(),
        fingerprint="fp",
    )


@pytest.mark.asyncio
async def test_app_mount_with_project_arg() -> None:
    from opsx_tui.presentation.app import OpsxTuiApp

    root = Path("/tmp/test-opsx-mount")
    root.mkdir(parents=True, exist_ok=True)
    (root / "openspec").mkdir(parents=True, exist_ok=True)
    (root / "openspec" / "config.yaml").write_text("schema_version: 1")

    container = MagicMock(spec=Container)
    ws_service = MagicMock()
    ws_service.read_snapshot.return_value = _make_snapshot(root)
    container.create_workspace_service.return_value = ws_service
    container.create_metadata_store.return_value = MagicMock()
    container.enrich_snapshot.return_value = _make_snapshot(root)

    watcher_mock = MagicMock()

    async def fake_stop() -> None:
        return None
    watcher_mock.stop = fake_stop
    container.create_workspace_watcher_service.return_value = watcher_mock

    app = OpsxTuiApp(container=container, project_arg=root)
    async with app.run_test() as pilot:
        assert app.opsx_project is not None
        assert app.opsx_project.project.root == root
        assert app.opsx_project.workspace.config_yaml
        assert len(app.query("#shell-header")) == 1
        await pilot.press("q")


@pytest.mark.asyncio
async def test_app_mount_with_auto_discovery() -> None:
    from opsx_tui.presentation.app import OpsxTuiApp

    root = Path("/tmp/test-opsx-autodiscover")
    root.mkdir(parents=True, exist_ok=True)
    (root / "openspec").mkdir(parents=True, exist_ok=True)
    (root / "openspec" / "config.yaml").write_text("schema_version: 1")

    container = MagicMock(spec=Container)
    discovery_service = MagicMock()
    discovery_service.discover.return_value = _make_valid_project(root)
    container.create_project_discovery_service.return_value = discovery_service
    ws_service = MagicMock()
    ws_service.read_snapshot.return_value = _make_snapshot(root)
    container.create_workspace_service.return_value = ws_service
    container.create_metadata_store.return_value = MagicMock()
    container.enrich_snapshot.return_value = _make_snapshot(root)

    watcher_mock = MagicMock()

    async def fake_stop() -> None:
        return None
    watcher_mock.stop = fake_stop
    container.create_workspace_watcher_service.return_value = watcher_mock

    app = OpsxTuiApp(container=container, project_arg=None)
    async with app.run_test() as pilot:
        assert app.opsx_project is not None
        assert len(app.query("#shell-header")) == 1
        await pilot.press("q")


@pytest.mark.asyncio
async def test_app_mount_discovery_fails_exits() -> None:
    from opsx_tui.presentation.app import OpsxTuiApp

    container = MagicMock(spec=Container)
    discovery_service = MagicMock()
    discovery_service.discover.return_value = None
    container.create_project_discovery_service.return_value = discovery_service

    app = OpsxTuiApp(container=container, project_arg=None)
    async with app.run_test():
        assert app.opsx_project is None
    assert not app._running
