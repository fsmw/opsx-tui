from __future__ import annotations

from collections.abc import Iterable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Static

from opsx_tui.domain.workspace import Change
from opsx_tui.presentation.views.change_detail_panel import ChangeDetailPanel


class BoardDetailModal(Screen[None]):
    """Full-screen modal showing the ChangeDetailPanel for a board card.

    Pushed via ``push_screen`` from BoardView; ``Escape`` pops it and focus
    returns to the previously selected card.
    """

    BINDINGS = [
        Binding("escape", "close_detail", "Close", priority=True),
    ]

    def __init__(self, change: Change) -> None:
        super().__init__(id="board-detail-modal")
        self._change: Change = change

    def compose(self) -> ComposeResult:
        with Vertical(id="board-detail-modal"):
            yield Static(
                f"## Change: {self._change.name}\n",
                id="board-detail-title",
            )
            yield ChangeDetailPanel(id="board-detail-panel")

    def on_mount(self) -> None:
        panel = self.query_one("#board-detail-panel", ChangeDetailPanel)
        panel.show_change(self._change)

    def action_close_detail(self) -> None:
        self.app.pop_screen()
