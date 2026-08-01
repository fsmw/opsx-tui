from __future__ import annotations

import hashlib
from pathlib import Path

from opsx_tui.application.lifecycle_service import LifecycleService
from opsx_tui.domain.change_parser import (
    ParsedDesign,
    ParsedProposal,
    ParsedTaskList,
    parse_design_markdown,
    parse_proposal_markdown,
    parse_task_markdown,
)
from opsx_tui.domain.errors import WorkspaceReadError
from opsx_tui.domain.ports import WorkspaceReader
from opsx_tui.domain.project import Diagnostic, DiagnosticLevel
from opsx_tui.domain.spec_parser import parse_spec_markdown
from opsx_tui.domain.status import ChangeStatus
from opsx_tui.domain.workspace import (
    ArtifactInfo,
    ArtifactKind,
    CanonicalSpec,
    Change,
    WorkspaceSnapshot,
)

_ARTIFACT_KINDS: dict[str, ArtifactKind] = {
    "proposal.md": ArtifactKind.PROPOSAL,
    "design.md": ArtifactKind.DESIGN,
    "tasks.md": ArtifactKind.TASKS,
}


class FilesystemWorkspaceReader(WorkspaceReader):
    def __init__(self, lifecycle_service: LifecycleService) -> None:
        self._lifecycle_service = lifecycle_service

    def read_workspace(self, openspec_root: Path) -> WorkspaceSnapshot:
        if not openspec_root.exists():
            raise WorkspaceReadError(openspec_root, "path does not exist")
        if not openspec_root.is_dir():
            raise WorkspaceReadError(openspec_root, "path is not a directory")

        diagnostics: list[Diagnostic] = []

        config_yaml = (openspec_root / "config.yaml").exists()
        if not config_yaml:
            diagnostics.append(Diagnostic(
                level=DiagnosticLevel.WARNING,
                message="openspec/config.yaml not found",
            ))

        specs = self._scan_specs(openspec_root, diagnostics)
        changes_dir = openspec_root / "changes"
        active_changes = self._scan_changes(changes_dir, diagnostics, archived=False)
        archived_changes = self._scan_changes(
            changes_dir / "archive", diagnostics, archived=True
        )
        fingerprint = self._compute_fingerprint(openspec_root)

        return WorkspaceSnapshot(
            root=openspec_root.parent,
            openspec_root=openspec_root,
            config_yaml=config_yaml,
            specs=specs,
            active_changes=active_changes,
            archived_changes=archived_changes,
            diagnostics=tuple(diagnostics),
            fingerprint=fingerprint,
        )

    def _scan_specs(
        self, openspec_root: Path, diagnostics: list[Diagnostic]
    ) -> tuple[CanonicalSpec, ...]:
        specs_dir = openspec_root / "specs"
        if not specs_dir.is_dir():
            return ()

        result: list[CanonicalSpec] = []
        for entry in sorted(specs_dir.iterdir()):
            if not entry.is_dir():
                diagnostics.append(Diagnostic(
                    level=DiagnosticLevel.WARNING,
                    message=f"Unexpected file in specs/: {entry.name}",
                ))

                continue
            spec_file = entry / "spec.md"
            abs_spec_file = None
            raw_markdown = None
            parsed = None
            if spec_file.exists():
                abs_spec_file = spec_file.resolve()
                try:
                    raw_markdown = spec_file.read_text(encoding="utf-8")
                    parsed = parse_spec_markdown(raw_markdown, entry.name)
                except OSError:
                    diagnostics.append(Diagnostic(
                        level=DiagnosticLevel.WARNING,
                        message=f"Failed to read spec file: {spec_file}",
                    ))
            else:
                diagnostics.append(Diagnostic(
                    level=DiagnosticLevel.WARNING,
                    message=f"Spec directory {entry.name} has no spec.md",
                ))
            result.append(CanonicalSpec(
                name=entry.name,
                spec_dir=entry,
                spec_file=spec_file if spec_file.exists() else None,
                absolute_spec_dir=entry.resolve(),
                absolute_spec_file=abs_spec_file,
                raw_markdown=raw_markdown,
                parsed=parsed,
            ))

        return tuple(result)

    def _scan_changes(
        self, changes_dir: Path, diagnostics: list[Diagnostic], archived: bool
    ) -> tuple[Change, ...]:
        if not changes_dir.is_dir():
            return ()

        result: list[Change] = []
        try:
            entries = list(changes_dir.iterdir())
        except PermissionError:
            diagnostics.append(Diagnostic(
                level=DiagnosticLevel.ERROR,
                message=f"Cannot read directory: {changes_dir}",
            ))

            return ()

        for entry in sorted(entries):
            if entry.name == "archive":
                continue
            if not entry.is_dir():
                diagnostics.append(Diagnostic(
                    level=DiagnosticLevel.WARNING,
                    message=f"Unexpected file in changes/: {entry.name}",
                ))
                continue
            artifacts = self._scan_artifacts(entry, diagnostics)
            delta_specs = self._scan_delta_specs(entry, diagnostics)
            parsed_proposal, parsed_design, parsed_tasks, artifact_diags = (
                self._parse_artifact_contents(entry, artifacts)
            )
            change = Change(
                name=entry.name,
                change_dir=entry,
                absolute_change_dir=entry.resolve(),
                artifacts=artifacts,
                is_archived=archived,
                delta_specs=delta_specs,
                state=ChangeStatus.UNKNOWN,
                parsed_proposal=parsed_proposal,
                parsed_design=parsed_design,
                parsed_tasks=parsed_tasks,
                artifact_diagnostics=tuple(artifact_diags),
            )
            assessment = self._lifecycle_service.assess(change)
            result.append(change.model_copy(update={"state": assessment.status}))
        return tuple(result)

    def _scan_delta_specs(
        self, change_dir: Path, diagnostics: list[Diagnostic]
    ) -> tuple[CanonicalSpec, ...]:
        specs_dir = change_dir / "specs"
        if not specs_dir.is_dir():
            return ()

        result: list[CanonicalSpec] = []
        spec_mds = sorted(specs_dir.rglob("spec.md"))
        for sp in spec_mds:
            try:
                raw_markdown = sp.read_text(encoding="utf-8")
            except OSError:
                diagnostics.append(Diagnostic(
                    level=DiagnosticLevel.WARNING,
                    message=f"Failed to read delta spec: {sp}",
                ))
                continue
            spec_name = sp.parent.name
            parsed = parse_spec_markdown(raw_markdown, spec_name)
            result.append(CanonicalSpec(
                name=spec_name,
                spec_dir=sp.parent,
                spec_file=sp,
                absolute_spec_dir=sp.parent.resolve(),
                absolute_spec_file=sp.resolve(),
                raw_markdown=raw_markdown,
                parsed=parsed,
            ))
        return tuple(result)

    def _scan_artifacts(
        self, change_dir: Path, diagnostics: list[Diagnostic]
    ) -> tuple[ArtifactInfo, ...]:
        result: list[ArtifactInfo] = []

        for filename, kind in _ARTIFACT_KINDS.items():
            path = change_dir / filename
            exists = path.exists()
            if not exists:
                diagnostics.append(Diagnostic(
                    level=DiagnosticLevel.WARNING,
                    message=f"Change {change_dir.name} is missing {filename}",
                ))
            result.append(ArtifactInfo(
                kind=kind,
                path=path,
                absolute_path=path.resolve() if exists else path,
                exists=exists,
            ))

        specs_dir = change_dir / "specs"
        if specs_dir.is_dir():
            spec_mds = list(specs_dir.rglob("*.md"))
            for sp in spec_mds:
                result.append(ArtifactInfo(
                    kind=ArtifactKind.SPECS,
                    path=sp,
                    absolute_path=sp.resolve(),
                    exists=True,
                ))
        elif not specs_dir.exists():
                diagnostics.append(Diagnostic(
                    level=DiagnosticLevel.WARNING,
                    message=f"Change {change_dir.name} has no specs/ directory",
                ))


        return tuple(result)

    def _parse_artifact_contents(
        self, change_dir: Path, artifacts: tuple[ArtifactInfo, ...]
    ) -> tuple[ParsedProposal | None, ParsedDesign | None,
                ParsedTaskList | None, list[Diagnostic]]:
        parsed_proposal: ParsedProposal | None = None
        parsed_design: ParsedDesign | None = None
        parsed_tasks: ParsedTaskList | None = None
        diags: list[Diagnostic] = []

        for artifact in artifacts:
            if not artifact.exists:
                continue
            try:
                content = artifact.absolute_path.read_text(encoding="utf-8")
            except OSError as e:
                msg = f"Failed to read {artifact.kind} at {artifact.absolute_path}: {e}"
                diags.append(Diagnostic(level=DiagnosticLevel.ERROR, message=msg))
                continue

            if artifact.kind == ArtifactKind.PROPOSAL:
                parsed_proposal = parse_proposal_markdown(content)
            elif artifact.kind == ArtifactKind.DESIGN:
                parsed_design = parse_design_markdown(content)
            elif artifact.kind == ArtifactKind.TASKS:
                parsed_tasks = parse_task_markdown(content)

        return parsed_proposal, parsed_design, parsed_tasks, diags

    @staticmethod
    def _compute_fingerprint(openspec_root: Path) -> str:
        entries: list[str] = []
        try:
            for p in sorted(openspec_root.rglob("*")):
                if p.is_file():
                    mtime = int(p.stat().st_mtime)
                    rel = p.relative_to(openspec_root)
                    entries.append(f"{rel}:{mtime}")
        except OSError:
            return ""
        if not entries:
            return ""
        raw = "\n".join(entries)
        return hashlib.sha256(raw.encode()).hexdigest()
