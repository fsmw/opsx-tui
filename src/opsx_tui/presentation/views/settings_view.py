from __future__ import annotations

from collections.abc import Iterable
from textual.widgets import Label, Static
from textual.widget import Widget

from opsx_tui.domain.open_spec_project import OpenSpecProject
from opsx_tui.domain.openspec_cli import OpenSpecCLIInfo
from opsx_tui.domain.project import DiagnosticLevel


class SettingsView(Widget):
    def __init__(self, opsx_project: OpenSpecProject, id: str | None = None) -> None:
        super().__init__(id=id)
        self.opsx_project: OpenSpecProject = opsx_project

    def compose(self) -> Iterable[Widget]:
        yield Label("Settings", id="view-title")
        yield Static(self._cli_status(), id="cli-status")

    def _cli_status(self) -> str:
        cli: OpenSpecCLIInfo | None = getattr(self.app, "cli_info", None)
        if cli is None:
            return "OpenSpec CLI: detecting..."
        if cli.path is None:
            return "OpenSpec CLI: not found"
        errors = [d.message for d in cli.diagnostics if d.level == DiagnosticLevel.ERROR]
        warnings = [d.message for d in cli.diagnostics if d.level == DiagnosticLevel.WARNING]
        lines = [
            f"OpenSpec CLI: {cli.path}",
            f"Version: {cli.version or 'unknown'}",
            f"Compatible: {'yes' if cli.is_compatible else 'no'}",
            f"Commands: {len(cli.available_commands)} available",
        ]
        for msg in errors:
            lines.append(f"ERROR: {msg}")
        for msg in warnings:
            lines.append(f"WARN: {msg}")
        return "\n".join(lines)
