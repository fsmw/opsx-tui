from __future__ import annotations

from pathlib import Path

from opsx_tui.domain.ports import WorkspaceReader
from opsx_tui.domain.workspace import WorkspaceSnapshot


class WorkspaceService:
    def __init__(self, reader: WorkspaceReader) -> None:
        self._reader = reader

    def read_snapshot(self, openspec_root: Path) -> WorkspaceSnapshot:
        return self._reader.read_workspace(openspec_root)
