from __future__ import annotations

from pathlib import Path

from opsx_tui.domain.project import (
    Diagnostic,
    DiagnosticLevel,
    DiscoverySource,
    Project,
)


def validate_project(
    path: Path,
    source: DiscoverySource,
) -> Project | None:
    if not path.exists():
        return None

    openspec_root = path / "openspec"
    diagnostics: list[Diagnostic] = []

    if not openspec_root.exists():
        diagnostics.append(
            Diagnostic(
                level=DiagnosticLevel.ERROR,
                message=f"Directory 'openspec/' not found at {openspec_root}",
            )
        )
        return Project(
            root=path,
            openspec_root=openspec_root,
            discovery_source=source,
            is_valid=False,
            diagnostics=tuple(diagnostics),
        )

    config_yaml = openspec_root / "config.yaml"
    if not config_yaml.exists():
        diagnostics.append(
            Diagnostic(
                level=DiagnosticLevel.WARNING,
                message=f"openspec/config.yaml not found at {config_yaml}",
            )
        )

    return Project(
        root=path,
        openspec_root=openspec_root,
        discovery_source=source,
        is_valid=config_yaml.exists(),
        diagnostics=tuple(diagnostics),
    )
