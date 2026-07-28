from __future__ import annotations

from collections.abc import Iterable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Static

from opsx_tui.domain.metadata import ChangeMetadata, Priority
from opsx_tui.domain.ports import MetadataStore


class MetadataEditModal(Screen[bool]):
    BINDINGS = [
        Binding("f", "toggle_favorite", "Favorite"),
        Binding("1", "set_priority_1", "Low"),
        Binding("2", "set_priority_2", "Medium"),
        Binding("3", "set_priority_3", "High"),
        Binding("4", "set_priority_4", "Urgent"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        store: MetadataStore,
        change_name: str,
        current: ChangeMetadata | None,
    ) -> None:
        super().__init__()
        self._store = store
        self._change_name = change_name
        self._metadata = current or ChangeMetadata()

    def compose(self) -> Iterable[Static | Input | Button]:
        yield Static(f"## Edit Metadata: {self._change_name}\n", id="edit-title")
        yield Static(
            f"**Priority:** [1]Low [2]Medium [3]High [4]Urgent — Current: {self._metadata.priority.name}",
            id="priority-display",
        )
        yield Static("**Favorite:** press `f` to toggle", id="fav-display")
        yield Input(
            value=", ".join(self._metadata.tags),
            placeholder="Tags (comma-separated)",
            id="tags-input",
        )
        yield Input(
            value=self._metadata.notes or "",
            placeholder="Notes",
            id="notes-input",
        )
        yield Input(
            value=self._metadata.blocked_reason or "",
            placeholder="Blocked reason",
            id="blocked-input",
        )
        yield Button("Save", id="save-btn", variant="primary")
        yield Button("Cancel", id="cancel-btn")

    def action_toggle_favorite(self) -> None:
        self._metadata = self._metadata.model_copy(
            update={"favorite": not self._metadata.favorite}
        )
        self._update_display()

    def action_set_priority_1(self) -> None:
        self._set_priority(Priority.LOW)

    def action_set_priority_2(self) -> None:
        self._set_priority(Priority.MEDIUM)

    def action_set_priority_3(self) -> None:
        self._set_priority(Priority.HIGH)

    def action_set_priority_4(self) -> None:
        self._set_priority(Priority.URGENT)

    def _set_priority(self, p: Priority) -> None:
        self._metadata = self._metadata.model_copy(update={"priority": p})
        self._update_display()

    def action_cancel(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self._do_save()
        elif event.button.id == "cancel-btn":
            self.dismiss(False)

    def _do_save(self) -> None:
        tags_str = self.query_one("#tags-input", Input).value
        notes = self.query_one("#notes-input", Input).value
        blocked = self.query_one("#blocked-input", Input).value
        tags = tuple(t.strip() for t in tags_str.split(",") if t.strip())
        final_meta = self._metadata.model_copy(
            update={
                "tags": tags,
                "notes": notes if notes else None,
                "blocked_reason": blocked if blocked else None,
            }
        )
        self._store.save(self._change_name, final_meta)
        self.dismiss(True)

    def _update_display(self) -> None:
        if not self.is_mounted:
            return
        fav_display = self.query_one("#fav-display", Static)
        pri_display = self.query_one("#priority-display", Static)
        pri_display.update(
            f"**Priority:** [1]Low [2]Medium [3]High [4]Urgent — Current: {self._metadata.priority.name}"
        )
        fav_display.update(
            f"**Favorite:** press `f` to toggle — {'★ Yes' if self._metadata.favorite else '☆ No'}"
        )
