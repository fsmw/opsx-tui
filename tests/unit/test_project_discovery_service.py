from __future__ import annotations

from pathlib import Path

from opsx_tui.application.project_discovery_service import ProjectDiscoveryService
from opsx_tui.domain.project import DiscoverySource, Project, ProjectDiscoveryStrategy


class _FakeStrategy(ProjectDiscoveryStrategy):
    def __init__(self, result: Project | None) -> None:
        self._result = result

    def discover(self) -> Project | None:
        return self._result


def test_short_circuit_with_cli_arg() -> None:
    service = ProjectDiscoveryService([])
    result = service.discover(cli_arg=Path("/nonexistent"))
    assert result is None


def test_returns_first_match() -> None:
    p1 = Project(
        root=Path("/a"),
        openspec_root=Path("/a/openspec"),
        discovery_source=DiscoverySource.ANCESTOR_WALK,
        is_valid=True,
    )
    p2 = Project(
        root=Path("/b"),
        openspec_root=Path("/b/openspec"),
        discovery_source=DiscoverySource.GIT_ROOT,
        is_valid=True,
    )
    service = ProjectDiscoveryService([_FakeStrategy(p1), _FakeStrategy(p2)])
    result = service.discover()
    assert result is not None
    assert result.root == Path("/a")


def test_all_strategies_return_none() -> None:
    service = ProjectDiscoveryService([_FakeStrategy(None), _FakeStrategy(None)])
    assert service.discover() is None


def test_empty_strategies() -> None:
    service = ProjectDiscoveryService([])
    assert service.discover() is None
