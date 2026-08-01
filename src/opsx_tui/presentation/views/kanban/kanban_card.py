from __future__ import annotations

from textual.widgets import Static

from opsx_tui.domain.workspace import Change
from opsx_tui.presentation.views.change_formatting import (
    artifact_icons,
    format_progress,
    metadata_prefix,
    state_abbrev,
)


class KanbanCard(Static):
    """A focusable card representing a single change on the board.

    The card is deliberately a projection: it renders read-only formatting
    from the change and never mutates lifecycle state (docs/05 §23.4).
    """

    can_focus = True

    def __init__(self, change: Change, id: str | None = None) -> None:
        super().__init__(id=id)
        self.change: Change = change

    def _warning_marker(self) -> str:
        if self.change.artifact_diagnostics or self.change.state.value == "blocked":
            return " \u26a0"
        return ""

    def render(self) -> str:
        state_str = state_abbrev(self.change.state.value)
        prog = format_progress(self.change.parsed_tasks)
        return (
            f"{metadata_prefix(self.change)}{self.change.name}\n"
            f"[{state_str}] {prog} {artifact_icons(self.change)}{self._warning_marker()}"
        )
