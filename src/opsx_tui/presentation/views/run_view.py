from __future__ import annotations

from collections.abc import Iterable
from textual.widgets import Label
from textual.widget import Widget

from opsx_tui.domain.open_spec_project import OpenSpecProject


class RunView(Widget):
    def __init__(self, opsx_project: OpenSpecProject, id: str | None = None) -> None:
        super().__init__(id=id)
        self.opsx_project: OpenSpecProject = opsx_project

    def compose(self) -> Iterable[Widget]:
        yield Label("Runner", id="view-title")
