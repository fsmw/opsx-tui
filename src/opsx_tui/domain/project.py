from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel


class DiscoverySource(StrEnum):
    CLI_ARG = "cli_arg"
    ENV_VAR = "env_var"
    ANCESTOR_WALK = "ancestor_walk"
    GIT_ROOT = "git_root"
    RECENT_PROJECTS = "recent_projects"
    INTERACTIVE = "interactive"


class DiagnosticLevel(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Diagnostic(BaseModel):
    level: DiagnosticLevel
    message: str


class Project(BaseModel):
    root: Path
    openspec_root: Path
    discovery_source: DiscoverySource
    is_valid: bool
    diagnostics: tuple[Diagnostic, ...] = ()


class ProjectDiscoveryStrategy(Protocol):
    def discover(self) -> Project | None: ...
