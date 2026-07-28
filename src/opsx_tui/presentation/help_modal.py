from __future__ import annotations

from textual.app import ComposeResult
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Label


class HelpModal(Screen):
    def compose(self) -> ComposeResult:
        yield Label(
            "=== Keyboard Bindings ===\n\n"
            "1-6     Switch views (Board/Specs/Changes/Runner/Logs/Settings)\n"
            "q       Quit\n"
            "Ctrl+C  Quit\n"
            "?       Toggle this help\n"
            "\nPress any key to close.",
            id="help-text",
        )

    def on_key(self, event: Key) -> None:
        self.dismiss()
