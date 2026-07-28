from __future__ import annotations

from textual.reactive import reactive
from textual.widgets import Header
from textual.widget import Widget


class OpsxHeader(Widget):
    active_view: reactive[str] = reactive("Board")

    def __init__(self, project_path: str, id: str | None = None) -> None:
        super().__init__(id=id)
        self._project_path = project_path

    def render(self) -> str:
        truncated = self._project_path
        if len(truncated) > 50:
            truncated = "..." + truncated[-47:]
        return f" OPSX TUI  │  {truncated}  │  {self.active_view}"
