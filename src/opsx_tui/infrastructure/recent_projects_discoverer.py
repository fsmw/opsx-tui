from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from platformdirs import PlatformDirs

from opsx_tui.domain.project import DiscoverySource, Project, ProjectDiscoveryStrategy
from opsx_tui.infrastructure.validation import validate_project

_MAX_RECENT = 10
_DIRS = PlatformDirs("opsx-tui")


def _recent_projects_path() -> Path:
    return Path(_DIRS.user_data_dir) / "recent-projects.json"


class RecentProjectsDiscoverer(ProjectDiscoveryStrategy):
    def discover(self) -> Project | None:
        path = _recent_projects_path()
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None
        entries: list[dict[str, Any]] = data.get("recent_projects", [])
        for entry in entries:
            raw = entry.get("path")
            if not raw:
                continue
            project = validate_project(Path(raw), DiscoverySource.RECENT_PROJECTS)
            if project is not None and project.is_valid:
                return project
        return None


def write_recent_project(project_root: Path) -> None:
    path = _recent_projects_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        raw = path.read_text()
        current: list[dict[str, Any]] = json.loads(raw).get("recent_projects", [])
    except (json.JSONDecodeError, FileNotFoundError, OSError):
        current = []
    entry = {
        "path": str(project_root.resolve()),
        "last_opened": datetime.now(UTC).isoformat(),
    }
    filtered = [e for e in current if e.get("path") != entry["path"]]
    filtered.insert(0, entry)
    path.write_text(json.dumps({"recent_projects": filtered[:_MAX_RECENT]}, indent=2))
