from __future__ import annotations

from pathlib import Path

import pytest
from textual.app import App, ComposeResult
from textual.widgets import TabbedContent

from opsx_tui.domain.open_spec_project import OpenSpecProject
from opsx_tui.domain.project import DiscoverySource, Project
from opsx_tui.domain.workspace import WorkspaceSnapshot
from opsx_tui.presentation.shell_screen import ShellScreen
from opsx_tui.presentation.widgets.opsx_header import OpsxHeader


@pytest.fixture
def opsx_project() -> OpenSpecProject:
    root = Path("/tmp/test-opsx-shell")
    project = Project(
        root=root,
        openspec_root=root / "openspec",
        discovery_source=DiscoverySource.CLI_ARG,
        is_valid=True,
    )
    snapshot = WorkspaceSnapshot(
        root=root,
        openspec_root=root / "openspec",
        config_yaml=True,
        specs=(),
        active_changes=(),
        archived_changes=(),
        diagnostics=(),
        fingerprint="fp",
    )
    return OpenSpecProject(project=project, workspace=snapshot)


# --- 8.1-8.3: OpsxHeader tests ---


class HeaderTestApp(App):
    def __init__(self, project_path: str = "/tmp/test") -> None:
        super().__init__()
        self._path = project_path

    def compose(self) -> ComposeResult:
        yield OpsxHeader(self._path, id="test-header")


async def test_header_renders_app_name() -> None:
    app = HeaderTestApp()
    async with app.run_test(size=(80, 10)):
        header = app.query_one("#test-header", OpsxHeader)
        rendered = header.render()
        assert "OPSX TUI" in rendered


async def test_header_shows_project_path() -> None:
    path = "/home/user/projects/test-opsx-project"
    app = HeaderTestApp(path)
    async with app.run_test(size=(80, 10)):
        header = app.query_one("#test-header", OpsxHeader)
        rendered = header.render()
        assert path in rendered


async def test_header_truncates_long_path() -> None:
    long_path = "/home/user/projects/" + "x" * 50
    app = HeaderTestApp(long_path)
    async with app.run_test(size=(80, 10)):
        header = app.query_one("#test-header", OpsxHeader)
        rendered = header.render()
        assert len(rendered.split("│")[1].strip()) <= 53


async def test_header_reactive_active_view() -> None:
    app = HeaderTestApp()
    async with app.run_test(size=(80, 10)):
        header = app.query_one("#test-header", OpsxHeader)
        assert header.active_view == "Board"
        header.active_view = "Specs"
        rendered = header.render()
        assert "Specs" in rendered


# --- 8.4: View widgets ---


async def test_board_view_shows_columns(opsx_project: OpenSpecProject) -> None:
    from opsx_tui.presentation.views.board_view import BoardView
    from opsx_tui.presentation.views.kanban.kanban_column import KanbanColumn

    app = App()
    app.opsx_project = opsx_project  # type: ignore[attr-defined]
    async with app.run_test(size=(120, 40)):
        await app.mount(BoardView(opsx_project))
        columns = app.query(KanbanColumn)
        assert len(columns) >= 7


async def test_specs_view_shows_title(opsx_project: OpenSpecProject) -> None:
    from opsx_tui.presentation.views.specs_view import SpecsView

    app = App()
    async with app.run_test(size=(80, 24)):
        await app.mount(SpecsView(opsx_project))
        search = app.query_one("#spec-search")
        assert search is not None


async def test_changes_view_has_search_input(opsx_project: OpenSpecProject) -> None:
    from opsx_tui.presentation.views.changes_view import ChangesView

    app = App()
    async with app.run_test(size=(80, 24)):
        await app.mount(ChangesView(opsx_project))
        inp = app.query_one("#change-search")
        assert inp is not None


async def test_run_view_shows_title(opsx_project: OpenSpecProject) -> None:
    from opsx_tui.presentation.views.run_view import RunView

    app = App()
    async with app.run_test(size=(40, 10)):
        await app.mount(RunView(opsx_project))
        label = app.query_one("#view-title")
        assert "Runner" in str(label.renderable)


async def test_logs_view_shows_title(opsx_project: OpenSpecProject) -> None:
    from opsx_tui.presentation.views.logs_view import LogsView

    app = App()
    async with app.run_test(size=(40, 10)):
        await app.mount(LogsView(opsx_project))
        label = app.query_one("#view-title")
        assert "Logs" in str(label.renderable)


async def test_settings_view_shows_title(opsx_project: OpenSpecProject) -> None:
    from opsx_tui.presentation.views.settings_view import SettingsView

    app = App()
    async with app.run_test(size=(40, 10)):
        await app.mount(SettingsView(opsx_project))
        label = app.query_one("#view-title")
        assert "Settings" in str(label.renderable)


# --- 8.5-8.9: ShellScreen tests ---


def _shell_app(project: OpenSpecProject) -> App:
    app = App()
    app.opsx_project = project  # type: ignore[attr-defined]
    return app


async def test_shell_screen_composes_all_elements(
    opsx_project: OpenSpecProject,
) -> None:
    app = _shell_app(opsx_project)
    async with app.run_test(size=(80, 24)):
        await app.push_screen(ShellScreen(opsx_project))
        assert len(app.query("#shell-header")) == 1
        tabs = app.query_one(TabbedContent)
        assert tabs is not None
        assert tabs.tab_count >= 6


async def test_key_1_switches_to_board(opsx_project: OpenSpecProject) -> None:
    app = _shell_app(opsx_project)
    async with app.run_test(size=(80, 24)) as pilot:
        await app.push_screen(ShellScreen(opsx_project))
        # wait for the screen to mount and compose
        await pilot.pause()
        tabs = app.query_one(TabbedContent)
        assert tabs.active == "board"
        await pilot.press("2")
        assert tabs.active == "specs"
        await pilot.press("3")
        assert tabs.active == "changes"
        await pilot.press("4")
        assert tabs.active == "runner"
        await pilot.press("5")
        assert tabs.active == "logs"
        await pilot.press("6")
        assert tabs.active == "settings"
        await pilot.press("1")
        assert tabs.active == "board"


async def test_key_q_exits_on_shell(opsx_project: OpenSpecProject) -> None:
    app = _shell_app(opsx_project)
    async with app.run_test(size=(80, 24)) as pilot:
        await app.push_screen(ShellScreen(opsx_project))
        await pilot.pause()
        await pilot.press("q")
    assert not app._running


async def test_key_question_pushs_help(opsx_project: OpenSpecProject) -> None:
    app = _shell_app(opsx_project)
    async with app.run_test(size=(80, 24)) as pilot:
        await app.push_screen(ShellScreen(opsx_project))
        await pilot.press("?")
        help_text = app.query("#help-text")
        assert len(help_text) == 1


async def test_help_modal_dismisses(opsx_project: OpenSpecProject) -> None:
    app = _shell_app(opsx_project)
    async with app.run_test(size=(80, 24)) as pilot:
        ss = ShellScreen(opsx_project)
        await app.push_screen(ss)
        await pilot.press("?")
        assert len(app.query("#help-text")) == 1
        await pilot.press("space")
        assert len(app.query("#help-text")) == 0


# --- 8.10: ErrorModal ---


async def test_error_modal_shows_message() -> None:
    from opsx_tui.presentation.error_modal import ErrorModal

    app = App()
    async with app.run_test(size=(60, 10)):
        await app.push_screen(ErrorModal("Something went wrong"))
        msg = app.query_one("#error-message")
        assert "Something went wrong" in str(msg.renderable)
