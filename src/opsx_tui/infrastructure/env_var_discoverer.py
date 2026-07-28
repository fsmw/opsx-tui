from __future__ import annotations

import os
from pathlib import Path

from opsx_tui.domain.project import DiscoverySource, Project, ProjectDiscoveryStrategy
from opsx_tui.infrastructure.validation import validate_project


class EnvVarDiscoverer(ProjectDiscoveryStrategy):
    def __init__(self, env_var: str = "OPSX_TUI_PROJECT") -> None:
        self._env_var = env_var

    def discover(self) -> Project | None:
        raw = os.environ.get(self._env_var)
        if not raw:
            return None
        path = Path(raw).expanduser().resolve()
        return validate_project(path, DiscoverySource.ENV_VAR)
