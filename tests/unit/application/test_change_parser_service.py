from __future__ import annotations

from pathlib import Path

from opsx_tui.application.change_parser_service import ChangeParserService
from opsx_tui.domain.workspace import ArtifactInfo, ArtifactKind, Change


class TestChangeParserService:
    def test_parse_artifacts_valid(self) -> None:
        base = Path("tests/fixtures/change-parsing/valid")
        artifacts = (
            _mk_artifact(ArtifactKind.PROPOSAL, base / "proposal.md"),
            _mk_artifact(ArtifactKind.DESIGN, base / "design.md"),
            _mk_artifact(ArtifactKind.TASKS, base / "tasks.md"),
        )
        change = Change(
            name="valid", change_dir=base, absolute_change_dir=base.resolve(),
            artifacts=artifacts, is_archived=False,
        )
        service = ChangeParserService()
        proposal, design, tasks, diags = service.parse_artifacts(change)
        assert proposal is not None
        assert design is not None
        assert tasks is not None
        assert len(diags) == 0

    def test_parse_artifacts_incomplete(self) -> None:
        base = Path("tests/fixtures/change-parsing/incomplete")
        artifacts = (
            _mk_artifact(ArtifactKind.PROPOSAL, base / "proposal.md"),
            _mk_artifact(ArtifactKind.DESIGN, base / "design.md", exists=False),
            _mk_artifact(ArtifactKind.TASKS, base / "tasks.md", exists=False),
        )
        change = Change(
            name="incomplete", change_dir=base, absolute_change_dir=base.resolve(),
            artifacts=artifacts, is_archived=False,
        )
        service = ChangeParserService()
        proposal, design, tasks, diags = service.parse_artifacts(change)
        assert proposal is not None
        assert design is None
        assert tasks is None
        assert len(diags) == 0

    def test_parse_artifacts_idempotent(self) -> None:
        base = Path("tests/fixtures/change-parsing/valid")
        artifacts = (
            _mk_artifact(ArtifactKind.PROPOSAL, base / "proposal.md"),
            _mk_artifact(ArtifactKind.DESIGN, base / "design.md"),
            _mk_artifact(ArtifactKind.TASKS, base / "tasks.md"),
        )
        change = Change(
            name="valid", change_dir=base, absolute_change_dir=base.resolve(),
            artifacts=artifacts, is_archived=False,
        )
        service = ChangeParserService()
        p1, d1, t1, _ = service.parse_artifacts(change)
        p2, d2, t2, _ = service.parse_artifacts(change)
        assert p1 == p2
        assert d1 == d2
        assert t1 == t2

    def test_parse_change_with_malformed_artifacts(self) -> None:
        base = Path("tests/fixtures/change-parsing/malformed")
        artifacts = (
            _mk_artifact(ArtifactKind.PROPOSAL, base / "proposal.md"),
            _mk_artifact(ArtifactKind.DESIGN, base / "design.md"),
            _mk_artifact(ArtifactKind.TASKS, base / "tasks.md"),
        )
        change = Change(
            name="malformed", change_dir=base, absolute_change_dir=base.resolve(),
            artifacts=artifacts, is_archived=False,
        )
        service = ChangeParserService()
        proposal, design, tasks, diags = service.parse_artifacts(change)
        assert proposal is not None
        assert len(proposal.unknown_sections) > 0
        assert design is not None
        assert len(design.diagnostics) > 0
        assert tasks is not None
        assert tasks.total > 0


def _mk_artifact(
    kind: ArtifactKind, path: Path, exists: bool = True,
) -> ArtifactInfo:
    return ArtifactInfo(
        kind=kind,
        path=path,
        absolute_path=path.resolve() if exists else path,
        exists=exists,
    )
