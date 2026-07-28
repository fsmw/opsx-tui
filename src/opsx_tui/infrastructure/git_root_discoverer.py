from __future__ import annotations

import subprocess
from pathlib import Path

from opsx_tui.domain.project import DiscoverySource, Project, ProjectDiscoveryStrategy
from opsx_tui.infrastructure.validation import validate_project


class GitRootDiscoverer(ProjectDiscoveryStrategy):
    def discover(self) -> Project | None:
        root = self._try_git_rev_parse()
        if root is not None:
            return validate_project(root, DiscoverySource.GIT_ROOT)
        root = self._try_git_dir_walk()
        if root is not None:
            return validate_project(root, DiscoverySource.GIT_ROOT)
        return None

    def _try_git_rev_parse(self) -> Path | None:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return None
            return Path(result.stdout.strip())
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None

    def _try_git_dir_walk(self) -> Path | None:
        current = Path.cwd().resolve()
        for _ in range(20):
            dot_git = current / ".git"
            if dot_git.is_dir() or dot_git.is_file():
                return current
            parent = current.parent
            if parent == current:
                break
            current = parent
        return None
