from __future__ import annotations

from collections.abc import Sequence

from opsx_tui.domain.change_parser import (
    ParsedDesign,
    ParsedProposal,
    ParsedTaskList,
    parse_design_markdown,
    parse_proposal_markdown,
    parse_task_markdown,
)
from opsx_tui.domain.project import Diagnostic, DiagnosticLevel
from opsx_tui.domain.workspace import ArtifactKind, Change


class ChangeParserService:
    def parse_artifacts(
        self,
        change: Change,
    ) -> tuple[ParsedProposal | None, ParsedDesign | None,
                ParsedTaskList | None, Sequence[Diagnostic]]:
        diagnostics: list[Diagnostic] = []
        parsed_proposal: ParsedProposal | None = None
        parsed_design: ParsedDesign | None = None
        parsed_tasks: ParsedTaskList | None = None

        for artifact in change.artifacts:
            if not artifact.exists:
                continue

            try:
                content = artifact.absolute_path.read_text(encoding="utf-8")
            except OSError as e:
                msg = f"Failed to read {artifact.kind} at {artifact.absolute_path}: {e}"
                diagnostics.append(Diagnostic(level=DiagnosticLevel.ERROR, message=msg))
                continue

            if artifact.kind == ArtifactKind.PROPOSAL:
                parsed_proposal = parse_proposal_markdown(content)
            elif artifact.kind == ArtifactKind.DESIGN:
                parsed_design = parse_design_markdown(content)
            elif artifact.kind == ArtifactKind.TASKS:
                parsed_tasks = parse_task_markdown(content)

        return parsed_proposal, parsed_design, parsed_tasks, tuple(diagnostics)
