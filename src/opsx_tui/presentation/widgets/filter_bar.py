from __future__ import annotations

from collections.abc import Iterable
from typing import cast

from textual.app import ComposeResult
from textual.containers import HorizontalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Checkbox, Input, Static

from opsx_tui.domain.filtering import ChangeFilter
from opsx_tui.domain.status import ChangeStatus

_STATE_ORDER = (
    ChangeStatus.DRAFT,
    ChangeStatus.PLANNING,
    ChangeStatus.READY,
    ChangeStatus.APPLYING,
    ChangeStatus.VERIFICATION,
    ChangeStatus.READY_TO_ARCHIVE,
    ChangeStatus.BLOCKED,
)


class FiltersChanged(Message):
    """Posted by FilterBar whenever the active filter changes."""

    def __init__(self, filt: ChangeFilter) -> None:
        super().__init__()
        self.filt = filt


class FilterBar(Widget):
    """Presentational filter controls shared by the Changes view and the board.

    Owns its own ChangeFilter state and posts a FiltersChanged message on every
    change; consumers subscribe by implementing ``on_filters_changed``.
    """

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id)
        self._filter = ChangeFilter()

    def compose(self) -> Iterable[Widget]:
        yield Input(placeholder="Filter...", id="filter-text")
        with HorizontalScroll(id="filter-states"):
            for state in _STATE_ORDER:
                yield Checkbox(f"{state.value}", id=f"filter-state-{state.value}")
        yield Input(placeholder="Tags (comma-separated)", id="filter-tags")
        yield Checkbox("Show archived", id="filter-archived")
        yield Static("no filters", id="filter-indicator")
        yield Button("Clear", id="filter-clear")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "filter-text":
            self._filter = self._filter.model_copy(update={"text": event.value})
        elif event.input.id == "filter-tags":
            tags = tuple(t.strip() for t in event.value.split(",") if t.strip())
            self._filter = self._filter.model_copy(update={"tags": tags})
        else:
            return
        self._post_filters_changed()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "filter-archived":
            self._filter = self._filter.model_copy(
                update={"include_archived": event.value}
            )
        elif event.checkbox.id and event.checkbox.id.startswith("filter-state-"):
            state_value = event.checkbox.id.removeprefix("filter-state-")
            states = set(self._filter.states)
            if event.value:
                states.add(ChangeStatus(state_value))
            else:
                states.discard(ChangeStatus(state_value))
            self._filter = self._filter.model_copy(update={"states": frozenset(states)})
        else:
            return
        self._post_filters_changed()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "filter-clear":
            self.action_clear_filters()

    def action_clear_filters(self) -> None:
        self._filter = ChangeFilter()
        text = self.query_one("#filter-text", Input)
        text.value = ""
        tags = self.query_one("#filter-tags", Input)
        tags.value = ""
        archived = self.query_one("#filter-archived", Checkbox)
        archived.value = False
        for checkbox in self.query("#filter-states Checkbox"):
            cast(Checkbox, checkbox).value = False
        self._post_filters_changed()

    def _post_filters_changed(self) -> None:
        self._update_indicator()
        self.post_message(FiltersChanged(self._filter))

    def _update_indicator(self) -> None:
        indicator = self.query_one("#filter-indicator", Static)
        if self._filter.is_active():
            indicator.update(f"{self._active_count()} filter(s) active")
        else:
            indicator.update("no filters")

    def _active_count(self) -> int:
        count = 0
        if self._filter.text:
            count += 1
        if self._filter.tags:
            count += 1
        if self._filter.include_archived:
            count += 1
        if self._filter.states:
            count += 1
        return count
