from __future__ import annotations

from pathlib import Path

from opsx_tui.domain.project import (
    Diagnostic,
    DiagnosticLevel,
    DiscoverySource,
    Project,
)


def test_discovery_source_values() -> None:
    assert DiscoverySource.CLI_ARG.value == "cli_arg"
    assert DiscoverySource.ENV_VAR.value == "env_var"
    assert DiscoverySource.ANCESTOR_WALK.value == "ancestor_walk"
    assert DiscoverySource.GIT_ROOT.value == "git_root"
    assert DiscoverySource.RECENT_PROJECTS.value == "recent_projects"
    assert DiscoverySource.INTERACTIVE.value == "interactive"


def test_diagnostic_level_values() -> None:
    assert DiagnosticLevel.INFO.value == "info"
    assert DiagnosticLevel.WARNING.value == "warning"
    assert DiagnosticLevel.ERROR.value == "error"


def test_diagnostic_creation() -> None:
    d = Diagnostic(level=DiagnosticLevel.WARNING, message="test warning")
    assert d.level == DiagnosticLevel.WARNING
    assert d.message == "test warning"


def test_project_valid() -> None:
    project = Project(
        root=Path("/fake/root"),
        openspec_root=Path("/fake/root/openspec"),
        discovery_source=DiscoverySource.CLI_ARG,
        is_valid=True,
    )
    assert project.is_valid is True
    assert project.discovery_source == DiscoverySource.CLI_ARG


def test_project_invalid() -> None:
    project = Project(
        root=Path("/fake/root"),
        openspec_root=Path("/fake/root/openspec"),
        discovery_source=DiscoverySource.ENV_VAR,
        is_valid=False,
        diagnostics=(
            Diagnostic(level=DiagnosticLevel.ERROR, message="openspec/ not found"),
        ),
    )
    assert project.is_valid is False
    assert len(project.diagnostics) == 1
