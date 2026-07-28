from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
from typing import Protocol

from opsx_tui.domain.config import Config
from opsx_tui.domain.metadata import ChangeMetadata
from opsx_tui.domain.openspec_cli import OpenSpecCLIInfo
from opsx_tui.domain.workspace import WorkspaceSnapshot


class ConfigLoader(Protocol):
    def load(self) -> Config: ...


class WorkspaceReader(Protocol):
    def read_workspace(self, openspec_root: Path) -> WorkspaceSnapshot: ...


class MetadataStore(Protocol):
    def load_all(self) -> dict[str, ChangeMetadata]: ...

    def save(self, change_name: str, metadata: ChangeMetadata) -> None: ...

    def delete(self, change_name: str) -> None: ...


class WorkspaceObserver(Protocol):
    def watch(self, path: Path) -> AsyncIterator[tuple[Path, ...]]: ...


class OpenSpecCLIDetector(Protocol):
    async def detect(self) -> OpenSpecCLIInfo: ...
