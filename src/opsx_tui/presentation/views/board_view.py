from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol, cast

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import HorizontalScroll, Vertical
from textual.widget import Widget

from opsx_tui.domain.filtering import ChangeFilter, filter_changes
from opsx_tui.domain.open_spec_project import OpenSpecProject
from opsx_tui.domain.workspace import Change
from opsx_tui.presentation.views.kanban.board_detail_modal import BoardDetailModal
from opsx_tui.presentation.views.kanban.kanban_card import KanbanCard
from opsx_tui.presentation.views.kanban.kanban_column import KanbanColumn
from opsx_tui.presentation.widgets.filter_bar import FilterBar, FiltersChanged


class _ProjectSource(Protocol):
    """The subset of the app the board reads for reactive refresh."""

    opsx_project: OpenSpecProject | None

_ACTIVE_STATES: tuple[str, ...] = (
    "draft",
    "planning",
    "ready",
    "applying",
    "verification",
    "ready-to-archive",
    "blocked",
)

_STATE_TITLES: dict[str, str] = {
    "draft": "Draft",
    "planning": "Planning",
    "ready": "Ready",
    "applying": "Applying",
    "verification": "Verification",
    "ready-to-archive": "Ready to Archive",
    "blocked": "Blocked",
    "unknown": "Unknown",
    "archived": "Archived",
}


class BoardView(Widget):
    """Kanban projection of active changes grouped by lifecycle state.

    The board is a read-only projection (docs/05 §2.3): it never assigns
    lifecycle state and never mutates the workspace.
    """

    BINDINGS = [
        Binding("up", "cursor_up", "Up", show=False, priority=True),
        Binding("down", "cursor_down", "Down", show=False, priority=True),
        Binding("left", "cursor_left", "Left", show=False, priority=True),
        Binding("right", "cursor_right", "Right", show=False, priority=True),
        Binding("enter", "open_detail", "Open detail"),
        Binding("c", "toggle_column", "Collapse/expand column"),
    ]

    def __init__(self, opsx_project: OpenSpecProject, id: str | None = None) -> None:
        super().__init__(id=id)
        self.opsx_project: OpenSpecProject = opsx_project
        self._columns: list[KanbanColumn] = []
        self._focused_column: int = 0
        self._active_filter: ChangeFilter = ChangeFilter()
        self._reloading: bool = False
        self._reload_pending: bool = False

    def compose(self) -> ComposeResult:
        with Vertical(id="board-layout"):
            yield FilterBar(id="board-filter-bar")
            with HorizontalScroll(id="kanban-board"):
                for state in _ACTIVE_STATES:
                    yield KanbanColumn(
                        state,
                        _STATE_TITLES[state],
                        id=f"column-{state}",
                    )

    async def on_mount(self) -> None:
        await self.reload()

    def on_filters_changed(self, event: FiltersChanged) -> None:
        self._active_filter = event.filt
        self.call_after_refresh(self.reload)

    async def reload(self) -> None:
        """Rebuild the board from the current app project (reactive refresh)."""
        if self._reloading:
            self._reload_pending = True
            return
        self._reloading = True
        try:
            await self._do_reload()
        finally:
            self._reloading = False
            if self._reload_pending:
                self._reload_pending = False
                await self.reload()

    async def _do_reload(self) -> None:
        project = cast(_ProjectSource, self.app).opsx_project
        if project is None:
            return
        filt = self._active_filter
        active = filter_changes(project.workspace.active_changes, filt)
        archived = filter_changes(project.workspace.archived_changes, filt)

        groups: dict[str, list[Change]] = {}
        for change in active:
            groups.setdefault(change.state.value, []).append(change)

        self._columns = list(self.query(KanbanColumn))
        for column in self._columns:
            state = column.state
            if state == "archived":
                continue
            changes = groups.get(state, [])
            changes.sort(key=self._sort_key)
            cards = [KanbanCard(c, id=f"card-{state}-{c.name}") for c in changes]
            await column.rebuild(cards)

        self._apply_state_column_visibility(groups)
        await self._sync_unknown_column(groups.get("unknown", []))
        await self._sync_archived_column(list(archived))

    def _apply_state_column_visibility(
        self, groups: dict[str, list[Change]]
    ) -> None:
        """Hide columns excluded by a state filter; always show the rest."""
        filt = self._active_filter
        for column in self._columns:
            if column.state == "archived":
                continue
            if filt.states:
                column.display = column.state in filt.states
            else:
                column.display = True

    async def _sync_unknown_column(self, changes: list[Change]) -> None:
        """Show an Unknown column only when unknown changes exist (§23.2)."""
        filt = self._active_filter
        if filt.states and "unknown" not in filt.states:
            changes = []
        board = self.query_one("#kanban-board")
        current_unknown: KanbanColumn | None = None
        for column in self.query(KanbanColumn):
            if column.state == "unknown":
                current_unknown = column
                break
        if changes:
            if current_unknown is None:
                current_unknown = KanbanColumn(
                    "unknown", _STATE_TITLES["unknown"], id="column-unknown"
                )
                await board.mount(current_unknown)
            changes.sort(key=self._sort_key)
            cards = [
                KanbanCard(c, id=f"card-unknown-{c.name}") for c in changes
            ]
            await current_unknown.rebuild(cards)
            current_unknown.display = True
        elif current_unknown is not None:
            await current_unknown.remove()

    async def _sync_archived_column(self, archived: list[Change]) -> None:
        """Show an Archived column when the archive filter is on (§23.1)."""
        board = self.query_one("#kanban-board")
        current_archived: KanbanColumn | None = None
        for column in self.query(KanbanColumn):
            if column.state == "archived":
                current_archived = column
                break
        if archived:
            if current_archived is None:
                current_archived = KanbanColumn(
                    "archived", _STATE_TITLES["archived"], id="column-archived"
                )
                await board.mount(current_archived)
            archived_sorted = sorted(archived, key=self._sort_key)
            cards = [
                KanbanCard(c, id=f"card-archived-{c.name}")
                for c in archived_sorted
            ]
            await current_archived.rebuild(cards)
            current_archived.display = True
        elif current_archived is not None:
            await current_archived.remove()

    def _sort_key(self, change: Change) -> tuple[tuple[int, ...], str]:
        meta = change.metadata
        if meta and meta.order:
            return ((0, meta.order), change.name)
        priority = -(meta.priority.value if meta else 0)
        blocked = 0 if change.state.value == "blocked" else 1
        favorite = 0 if (meta and meta.favorite) else 1
        return ((1, priority, blocked, favorite), change.name)

    def _focused_column_index(self) -> int:
        if not self._columns:
            return 0
        for i, column in enumerate(self._columns):
            if column.has_focus or any(
                card.has_focus for card in column._cards
            ):
                return i
        return self._focused_column

    def _focused_card(self, column: KanbanColumn) -> KanbanCard | None:
        for card in column._cards:
            if card.has_focus:
                return card
        return None

    def _focus_column_card(self, column: KanbanColumn) -> None:
        if column._cards:
            column._cards[0].focus()
        elif column.query("#column-header"):
            column.query_one("#column-header").focus()

    def action_cursor_down(self) -> None:
        if not self._columns:
            return
        column = self._columns[self._focused_column_index()]
        cards = column._cards
        if not cards:
            return
        focused = self._focused_card(column)
        idx = cards.index(focused) if focused in cards else -1
        target = cards[idx + 1] if idx + 1 < len(cards) else cards[0]
        target.focus()
        self._focused_column = self._columns.index(column)

    def action_cursor_up(self) -> None:
        if not self._columns:
            return
        column = self._columns[self._focused_column_index()]
        cards = column._cards
        if not cards:
            return
        focused = self._focused_card(column)
        idx = cards.index(focused) if focused in cards else 0
        target = cards[idx - 1] if idx > 0 else cards[-1]
        target.focus()
        self._focused_column = self._columns.index(column)

    def action_cursor_right(self) -> None:
        self._move_horizontal(1)

    def action_cursor_left(self) -> None:
        self._move_horizontal(-1)

    def _move_horizontal(self, delta: int) -> None:
        if not self._columns:
            return
        idx = self._focused_column_index()
        nxt = idx + delta
        if nxt < 0 or nxt >= len(self._columns):
            return
        self._focused_column = nxt
        self._focus_column_card(self._columns[nxt])

    def action_toggle_column(self) -> None:
        if not self._columns:
            return
        column = self._columns[self._focused_column_index()]
        column.toggle_collapsed()
        if not column.is_collapsed:
            self._focus_column_card(column)

    def action_open_detail(self) -> None:
        if not self._columns:
            return
        column = self._columns[self._focused_column_index()]
        card = self._focused_card(column)
        if card is None and column._cards:
            card = column._cards[0]
        if card is None:
            self.app.notify("No card selected", severity="warning", timeout=3)
            return
        self.app.push_screen(BoardDetailModal(card.change))
