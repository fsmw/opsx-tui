from __future__ import annotations

from pathlib import Path

from opsx_tui.domain.project import DiscoverySource, Project, ProjectDiscoveryStrategy
from opsx_tui.infrastructure.validation import validate_project


class AncestorDiscoverer(ProjectDiscoveryStrategy):
    def __init__(self, start_dir: Path | None = None, max_depth: int = 10) -> None:
        self._start_dir = start_dir or Path.cwd()
        self._max_depth = max_depth

    def discover(self) -> Project | None:
        current = self._start_dir.resolve()
        for _ in range(self._max_depth):
            if (current / "openspec").is_dir():
                return validate_project(current, DiscoverySource.ANCESTOR_WALK)
            parent = current.parent
            if parent == current:
                break
            current = parent
        return None
