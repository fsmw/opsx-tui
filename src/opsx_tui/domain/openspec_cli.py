from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from opsx_tui.domain.project import Diagnostic

CLI_VERSION_MINIMUM = (0, 1, 0)


class OpenSpecCLIInfo(BaseModel, frozen=True):
    path: Path | None = None
    version: str | None = None
    version_tuple: tuple[int, int, int] | None = None
    is_compatible: bool = False
    available_commands: frozenset[str] = frozenset()
    diagnostics: tuple[Diagnostic, ...] = ()
