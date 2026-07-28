from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import TabbedContent, TabPane

from opsx_tui.domain.open_spec_project import OpenSpecProject
from opsx_tui.presentation.views.board_view import BoardView
from opsx_tui.presentation.views.changes_view import ChangesView
from opsx_tui.presentation.views.logs_view import LogsView
from opsx_tui.presentation.views.run_view import RunView
from opsx_tui.presentation.views.settings_view import SettingsView
from opsx_tui.presentation.views.specs_view import SpecsView
from opsx_tui.presentation.widgets.opsx_footer import OpsxFooter
from opsx_tui.presentation.widgets.opsx_header import OpsxHeader


VIEW_TABS: dict[str, str] = {
    "1": "board",
    "2": "specs",
    "3": "changes",
    "4": "runner",
    "5": "logs",
    "6": "settings",
}


class ShellScreen(Screen):
    BINDINGS = [
        Binding("1", "switch_view('board')", "Board", show=False),
        Binding("2", "switch_view('specs')", "Specs", show=False),
        Binding("3", "switch_view('changes')", "Changes", show=False),
        Binding("4", "switch_view('runner')", "Runner", show=False),
        Binding("5", "switch_view('logs')", "Logs", show=False),
        Binding("6", "switch_view('settings')", "Settings", show=False),
        Binding("q", "app.exit", "Quit", priority=True),
        Binding("ctrl+c", "app.exit", "Quit", priority=True),
        Binding("?", "push_help", "Help", show=False),
    ]

    def __init__(self, opsx_project: OpenSpecProject) -> None:
        super().__init__()
        self.opsx_project: OpenSpecProject = opsx_project

    def compose(self) -> ComposeResult:
        yield OpsxHeader(str(self.opsx_project.project.root), id="shell-header")
        with TabbedContent(initial="board"):
            with TabPane("Board", id="board"):
                yield BoardView(self.opsx_project)
            with TabPane("Specs", id="specs"):
                yield SpecsView(self.opsx_project)
            with TabPane("Changes", id="changes"):
                yield ChangesView(self.opsx_project)
            with TabPane("Runner", id="runner"):
                yield RunView(self.opsx_project)
            with TabPane("Logs", id="logs"):
                yield LogsView(self.opsx_project)
            with TabPane("Settings", id="settings"):
                yield SettingsView(self.opsx_project)
        yield OpsxFooter()

    def action_switch_view(self, view: str) -> None:
        tabs = self.query_one(TabbedContent)
        tabs.active = view

    def on_tabbed_content_tab_activated(
        self, event: TabbedContent.TabActivated
    ) -> None:
        header = self.query_one(OpsxHeader)
        tab_id = event.tab.id
        if tab_id is not None:
            header.active_view = tab_id.capitalize()

    def action_push_help(self) -> None:
        from opsx_tui.presentation.help_modal import HelpModal

        self.app.push_screen(HelpModal())
