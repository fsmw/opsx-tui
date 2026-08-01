from __future__ import annotations

from collections.abc import Iterable

from textual.binding import Binding
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import ListItem, ListView, Static

from opsx_tui.domain.filtering import ChangeFilter, filter_changes
from opsx_tui.domain.open_spec_project import OpenSpecProject
from opsx_tui.domain.workspace import Change
from opsx_tui.presentation.views.change_detail_panel import ChangeDetailPanel
from opsx_tui.presentation.views.change_formatting import format_change_item
from opsx_tui.presentation.widgets.filter_bar import FilterBar, FiltersChanged

_format_change_item = format_change_item


class ChangesView(Widget):
    BINDINGS = [
        Binding("e", "edit_metadata", "Edit metadata", priority=True),
    ]

    def __init__(self, opsx_project: OpenSpecProject, id: str | None = None) -> None:
        super().__init__(id=id)
        self.opsx_project: OpenSpecProject = opsx_project
        self._selected_change: Change | None = None
        self._active_filter: ChangeFilter = ChangeFilter()

    def compose(self) -> Iterable[Widget]:
        yield FilterBar(id="change-filter-bar")
        with Horizontal(id="change-browser-panel"):
            yield ListView(id="change-list")
            yield ChangeDetailPanel(id="change-detail-panel")

    def _build_list_items(self, filt: ChangeFilter) -> list[ListItem]:
        def sort_key(c: Change) -> tuple[int, str]:
            return (c.metadata.order if c.metadata else 0, c.name)

        active = sorted(
            self.opsx_project.workspace.active_changes, key=sort_key
        )
        archived = sorted(
            self.opsx_project.workspace.archived_changes, key=sort_key
        )

        active_filtered = filter_changes(active, filt)
        archived_filtered = filter_changes(archived, filt)

        items: list[ListItem] = []
        for change in active_filtered:
            text = _format_change_item(change)
            items.append(ListItem(Static(text)))

        if archived_filtered:
            items.append(ListItem(Static("--- Archived ---")))
            for change in archived_filtered:
                text = _format_change_item(change)
                items.append(ListItem(Static(text)))

        return items

    async def on_mount(self) -> None:
        await self._rebuild_list()

    async def on_filters_changed(self, event: FiltersChanged) -> None:
        self._active_filter = event.filt
        await self._rebuild_list()

    async def _rebuild_list(self) -> None:
        lv = self.query_one("#change-list", ListView)
        await lv.remove_children(lv.children)
        items = self._build_list_items(self._active_filter)
        await lv.mount(*items)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item is None:
            return
        label = event.item.query_one(Static)
        label_text = str(label.renderable)
        if "---" in label_text:
            self._selected_change = None
            return
        workspace = self.opsx_project.workspace
        for change in list(workspace.active_changes) + list(workspace.archived_changes):
            if change.name in label_text:
                self._selected_change = change
                panel = self.query_one("#change-detail-panel", ChangeDetailPanel)
                panel.show_change(change)
                return

    def action_edit_metadata(self) -> None:
        if self._selected_change is None:
            self.app.notify("No change selected", severity="warning", timeout=3)
            return
        store = getattr(self.app, "_metadata_store", None)
        if store is None:
            self.app.notify(
                "Metadata store not available", severity="error", timeout=3
            )
            return
        from opsx_tui.presentation.modals.metadata_edit_modal import MetadataEditModal

        modal = MetadataEditModal(
            store=store,
            change_name=self._selected_change.name,
            current=self._selected_change.metadata,
        )

        def _on_result(result: bool | None) -> None:
            if result:
                self.call_after_refresh(self._rebuild_list)

        self.app.push_screen(modal, _on_result)
