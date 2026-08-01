from __future__ import annotations

from collections.abc import Iterable

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Static
from textual.widget import Widget

from opsx_tui.presentation.views.kanban.kanban_card import KanbanCard


class _FocusableHeader(Static):
    """Column header Static that can receive focus when the column is empty."""

    can_focus = True


class KanbanColumn(Widget):
    """A single lifecycle-state column on the board.

    Holds a header (title + live card count) and a scrollable list of
    KanbanCards. Collapse/expand is a transient visual state only and is
    never persisted (docs/05 §18.4).
    """

    def __init__(
        self,
        state: str,
        title: str,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self.state: str = state
        self.title: str = title
        self._collapsed: bool = False
        self._cards: list[KanbanCard] = []

    def compose(self) -> ComposeResult:
        yield _FocusableHeader(f"{self.title} (0)", id="column-header")
        yield VerticalScroll(id=f"cards-{self.state}")

    @property
    def is_collapsed(self) -> bool:
        return self._collapsed

    def toggle_collapsed(self) -> None:
        self._collapsed = not self._collapsed
        scroll = self.query_one(f"#cards-{self.state}", VerticalScroll)
        if self._collapsed:
            scroll.display = False
        else:
            scroll.display = True
        self._update_header()

    async def rebuild(self, cards: list[KanbanCard]) -> None:
        self._cards = cards
        scroll = self.query_one(f"#cards-{self.state}", VerticalScroll)
        await scroll.remove_children(scroll.children)
        await scroll.mount(*cards)
        if self._collapsed:
            scroll.display = False
        self._update_header()

    def _update_header(self) -> None:
        header = self.query_one("#column-header", Static)
        marker = "\u25be" if self._collapsed else ""
        header.update(f"{self.title} ({len(self._cards)}) {marker}")
