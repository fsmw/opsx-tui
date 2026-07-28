from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from opsx_tui.domain.project import DiscoverySource, Project, ProjectDiscoveryStrategy
from opsx_tui.infrastructure.validation import validate_project


class ProjectDiscoveryService:
    def __init__(self, strategies: Sequence[ProjectDiscoveryStrategy]) -> None:
        self._strategies = list(strategies)

    def discover(self, cli_arg: Path | None = None) -> Project | None:
        if cli_arg is not None:
            return validate_project(cli_arg, DiscoverySource.CLI_ARG)
        for strategy in self._strategies:
            result = strategy.discover()
            if result is not None:
                return result
        return None
