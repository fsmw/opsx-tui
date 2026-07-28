from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from opsx_tui.application.container import Container
from opsx_tui.domain.workspace import WorkspaceSnapshot


def _fake_snapshot(root: Path) -> WorkspaceSnapshot:
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


async def test_app_launches_without_project_exits_cleanly() -> None:
    from opsx_tui.presentation.app import OpsxTuiApp

    app = OpsxTuiApp(container=None)
    async with app.run_test(size=(80, 24)):
        assert app.screen is not None


async def test_app_exits_on_q() -> None:
    from opsx_tui.presentation.app import OpsxTuiApp

    app = OpsxTuiApp(container=None)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.press("q")
    assert not app._running


async def test_app_exits_on_ctrl_c() -> None:
    from opsx_tui.presentation.app import OpsxTuiApp

    app = OpsxTuiApp(container=None)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.press("ctrl+c")
    assert not app._running


async def test_app_with_project_pushes_shell_screen() -> None:
    from opsx_tui.presentation.app import OpsxTuiApp

    root = Path("/tmp/test-shell-project")
    root.mkdir(parents=True, exist_ok=True)
    (root / "openspec").mkdir(parents=True, exist_ok=True)
    (root / "openspec" / "config.yaml").write_text("schema_version: 1")

    container = MagicMock(spec=Container)
    ws_service = MagicMock()
    ws_service.read_snapshot.return_value = _fake_snapshot(root)
    container.create_workspace_service.return_value = ws_service
    container.create_metadata_store.return_value = MagicMock()
    container.enrich_snapshot.return_value = _fake_snapshot(root)
    watcher = MagicMock()

    async def fake_stop() -> None:
        return None
    watcher.stop = fake_stop
    container.create_workspace_watcher_service.return_value = watcher

    app = OpsxTuiApp(container=container, project_arg=root)
    async with app.run_test() as pilot:
        assert app.opsx_project is not None
        header = app.query("#shell-header")
        assert len(header) == 1
        await pilot.press("q")
