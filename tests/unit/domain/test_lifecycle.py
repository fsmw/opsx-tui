from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from opsx_tui.domain.change_parser import ParsedProposal, ParsedTaskItem, ParsedTaskList
from opsx_tui.domain.lifecycle import (
    BlockingCondition,
    ChangeStatus,
    LifecycleAssessment,
    LifecycleInput,
    RequiredArtifact,
    VerificationRecord,
    _applying_assessment,
    _archived_assessment,
    _blocked_assessment,
    _cannot_assess,
    _draft_assessment,
    _evaluate_blockers,
    _missing_required_artifacts,
    _no_tasks_completed,
    _planning_assessment,
    _proposal_missing_or_invalid,
    _ready_assessment,
    _ready_to_archive_assessment,
    _some_tasks_pending,
    _tasks_empty,
    _unknown_assessment,
    _verification_assessment,
    _verification_current_and_ok,
    assess_lifecycle,
)
from opsx_tui.domain.metadata import ChangeMetadata
from opsx_tui.domain.project import Diagnostic, DiagnosticLevel
from opsx_tui.domain.workspace import (
    ArtifactInfo,
    ArtifactKind,
    CanonicalSpec,
    Change,
)


def _spec(name: str = "auth") -> CanonicalSpec:
    return CanonicalSpec(
        name=name,
        spec_dir=Path(f"/fake/specs/{name}"),
        spec_file=Path(f"/fake/specs/{name}/spec.md"),
        absolute_spec_dir=Path(f"/fake/specs/{name}"),
        absolute_spec_file=Path(f"/fake/specs/{name}/spec.md"),
    )


def _proposal() -> ParsedProposal:
    return ParsedProposal(
        sections={"Why": "reason", "What Changes": "stuff"},
        known_sections=frozenset({"Why", "What Changes"}),
        unknown_sections=[],
        missing_sections=[],
        line_ranges={"Why": (1, 2), "What Changes": (3, 4)},
        diagnostics=(),
    )


_UNSET = object()


def _change(
    *,
    is_archived: bool = False,
    parsed_proposal: ParsedProposal | None = _UNSET,  # type: ignore[assignment]
    artifacts: tuple[ArtifactInfo, ...] | None = None,
    parsed_tasks: ParsedTaskList | None = None,
    artifact_diagnostics: tuple[Diagnostic, ...] = (),
    metadata: ChangeMetadata | None = None,
) -> Change:
    return Change(
        name="test-change",
        change_dir=Path("/fake/changes/test-change"),
        absolute_change_dir=Path("/fake/changes/test-change"),
        is_archived=is_archived,
        artifacts=artifacts or _all_artifacts(),
        parsed_proposal=(
            _proposal() if parsed_proposal is _UNSET else parsed_proposal
        ),
        parsed_tasks=parsed_tasks,
        artifact_diagnostics=artifact_diagnostics,
        metadata=metadata,
    )


def _all_artifacts() -> tuple[ArtifactInfo, ...]:
    return tuple(
        ArtifactInfo(
            kind=kind,
            path=Path(f"/fake/{kind.value}.md"),
            absolute_path=Path(f"/fake/{kind.value}.md"),
            exists=True,
        )
        for kind in ArtifactKind
    )


def _default_input(
    change: Change | None = None,
    verification: VerificationRecord | None = None,
    current_fingerprint: str = "abc123",
) -> LifecycleInput:
    return LifecycleInput(
        change=change or _change(),
        required_artifacts=(
            RequiredArtifact(name="proposal"),
            RequiredArtifact(name="design"),
            RequiredArtifact(name="specs"),
            RequiredArtifact(name="tasks"),
        ),
        verification=verification,
        current_fingerprint=current_fingerprint,
    )


class TestChangeStatus:
    def test_all_nine_states(self) -> None:
        assert set(ChangeStatus) == {
            ChangeStatus.DRAFT,
            ChangeStatus.PLANNING,
            ChangeStatus.READY,
            ChangeStatus.APPLYING,
            ChangeStatus.VERIFICATION,
            ChangeStatus.READY_TO_ARCHIVE,
            ChangeStatus.BLOCKED,
            ChangeStatus.ARCHIVED,
            ChangeStatus.UNKNOWN,
        }

    def test_values_are_kebab_case(self) -> None:
        assert ChangeStatus.DRAFT == "draft"
        assert ChangeStatus.READY_TO_ARCHIVE == "ready-to-archive"
        assert ChangeStatus.UNKNOWN == "unknown"


class TestRequiredArtifact:
    def test_defaults_to_required(self) -> None:
        ra = RequiredArtifact(name="proposal")
        assert ra.name == "proposal"
        assert ra.required is True

    def test_optional_artifact(self) -> None:
        ra = RequiredArtifact(name="docs", required=False)
        assert ra.required is False

    def test_frozen(self) -> None:
        ra = RequiredArtifact(name="proposal")
        with pytest.raises(ValidationError):
            ra.name = "design"  # type: ignore[misc]


class TestBlockingCondition:
    def test_defaults(self) -> None:
        bc = BlockingCondition(code="X", message="blocked")
        assert bc.severity == "error"
        assert bc.recoverable is True
        assert bc.suggested_actions == ()

    def test_custom(self) -> None:
        bc = BlockingCondition(
            code="MANUAL_BLOCK",
            message="Waiting for review",
            severity="warning",
            recoverable=True,
            suggested_actions=("unblock",),
        )
        assert bc.code == "MANUAL_BLOCK"
        assert bc.severity == "warning"
        assert bc.suggested_actions == ("unblock",)


class TestVerificationRecord:
    def test_defaults(self) -> None:
        vr = VerificationRecord(state="passed", fingerprint="abc")
        assert vr.state == "passed"
        assert vr.fingerprint == "abc"
        assert vr.assessed_at is None
        assert vr.findings is None


class TestLifecycleInput:
    def test_defaults(self) -> None:
        inp = _default_input()
        assert inp.openspec_state is None
        assert inp.backend_availability == ()
        assert inp.git_state is None
        assert inp.current_fingerprint == "abc123"


class TestLifecycleAssessment:
    def test_frozen(self) -> None:
        la = LifecycleAssessment(
            status=ChangeStatus.DRAFT,
            assessed_at=__import__("datetime").datetime.now(),
            input_fingerprint="abc",
        )
        with pytest.raises(ValidationError):
            la.status = ChangeStatus.READY  # type: ignore[misc]


# --- helpers ---


class TestProposalMissingOrInvalid:
    def test_true_when_no_proposal(self) -> None:
        c = _change(parsed_proposal=None)
        inp = _default_input(change=c)
        assert _proposal_missing_or_invalid(inp) is True

    def test_false_when_proposal_exists(self) -> None:
        c = _change(parsed_proposal=_proposal())
        assert _proposal_missing_or_invalid(_default_input(change=c)) is False


class TestMissingRequiredArtifacts:
    def test_none_missing(self) -> None:
        assert _missing_required_artifacts(_default_input()) is False

    def test_missing_design(self) -> None:
        arts = tuple(
            ArtifactInfo(
                kind=k,
                path=Path(f"/fake/{k.value}.md"),
                absolute_path=Path(f"/fake/{k.value}.md"),
                exists=True,
            )
            for k in (ArtifactKind.PROPOSAL, ArtifactKind.TASKS)
        )
        c = _change(artifacts=arts)
        assert _missing_required_artifacts(_default_input(change=c)) is True

    def test_artifact_not_exist(self) -> None:
        arts = tuple(
            ArtifactInfo(
                kind=k,
                path=Path(f"/fake/{k.value}.md"),
                absolute_path=Path(f"/fake/{k.value}.md"),
                exists=k != ArtifactKind.DESIGN,
            )
            for k in ArtifactKind
        )
        c = _change(artifacts=arts)
        assert _missing_required_artifacts(_default_input(change=c)) is True

    def test_optional_not_required(self) -> None:
        inp = _default_input()
        inp = LifecycleInput(
            change=inp.change,
            required_artifacts=(
                RequiredArtifact(name="proposal"),
                RequiredArtifact(name="custom", required=False),
            ),
        )
        assert _missing_required_artifacts(inp) is False


class TestTasksEmpty:
    def test_none_tasks(self) -> None:
        c = _change(parsed_tasks=None)
        assert _tasks_empty(_default_input(change=c)) is True

    def test_zero_total(self) -> None:
        from opsx_tui.domain.change_parser import ParsedTaskList

        pt = ParsedTaskList(
            items=(),
            total=0,
            completed=0,
            section_map={}, diagnostics=(),
        )
        c = _change(parsed_tasks=pt)
        assert _tasks_empty(_default_input(change=c)) is True

    def test_nonzero_total(self) -> None:
        from opsx_tui.domain.change_parser import ParsedTaskList

        pt = ParsedTaskList(
            items=(ParsedTaskItem(line_number=1, text="x", checked=False, section=""),),
            total=1,
            completed=0,
            section_map={}, diagnostics=(),
        )
        c = _change(parsed_tasks=pt)
        assert _tasks_empty(_default_input(change=c)) is False


class TestNoTasksCompleted:
    def test_none_tasks(self) -> None:
        c = _change(parsed_tasks=None)
        assert _no_tasks_completed(_default_input(change=c)) is True

    def test_zero_completed(self) -> None:
        from opsx_tui.domain.change_parser import ParsedTaskList

        pt = ParsedTaskList(
            items=(ParsedTaskItem(line_number=1, text="x", checked=False, section=""),),
            total=1,
            completed=0,
            section_map={}, diagnostics=(),
        )
        c = _change(parsed_tasks=pt)
        assert _no_tasks_completed(_default_input(change=c)) is True

    def test_some_completed(self) -> None:
        from opsx_tui.domain.change_parser import ParsedTaskList

        pt = ParsedTaskList(
            items=(ParsedTaskItem(line_number=1, text="x", checked=True, section=""),),
            total=1,
            completed=1,
            section_map={}, diagnostics=(),
        )
        c = _change(parsed_tasks=pt)
        assert _no_tasks_completed(_default_input(change=c)) is False


class TestSomeTasksPending:
    def test_none_tasks(self) -> None:
        c = _change(parsed_tasks=None)
        assert _some_tasks_pending(_default_input(change=c)) is False

    def test_some_done_some_pending(self) -> None:
        from opsx_tui.domain.change_parser import ParsedTaskList

        pt = ParsedTaskList(
            items=(
                ParsedTaskItem(line_number=1, text="a", checked=True, section=""),
                ParsedTaskItem(line_number=2, text="b", checked=False, section=""),
            ),
            total=2,
            completed=1,
            section_map={}, diagnostics=(),
        )
        c = _change(parsed_tasks=pt)
        assert _some_tasks_pending(_default_input(change=c)) is True

    def test_all_done(self) -> None:
        from opsx_tui.domain.change_parser import ParsedTaskList

        pt = ParsedTaskList(
            items=(ParsedTaskItem(line_number=1, text="a", checked=True, section=""),),
            total=1,
            completed=1,
            section_map={}, diagnostics=(),
        )
        c = _change(parsed_tasks=pt)
        assert _some_tasks_pending(_default_input(change=c)) is False

    def test_none_done(self) -> None:
        from opsx_tui.domain.change_parser import ParsedTaskList

        pt = ParsedTaskList(
            items=(ParsedTaskItem(line_number=1, text="a", checked=False, section=""),),
            total=1,
            completed=0,
            section_map={}, diagnostics=(),
        )
        c = _change(parsed_tasks=pt)
        assert _some_tasks_pending(_default_input(change=c)) is False


class TestVerificationCurrentAndOk:
    def test_no_verification(self) -> None:
        inp = _default_input(verification=None)
        assert _verification_current_and_ok(inp) is False

    def test_not_passed(self) -> None:
        vr = VerificationRecord(state="failed", fingerprint="abc123")
        inp = _default_input(verification=vr, current_fingerprint="abc123")
        assert _verification_current_and_ok(inp) is False

    def test_fingerprint_mismatch(self) -> None:
        vr = VerificationRecord(state="passed", fingerprint="abc123")
        inp = _default_input(verification=vr, current_fingerprint="xyz789")
        assert _verification_current_and_ok(inp) is False

    def test_passed_and_matching(self) -> None:
        vr = VerificationRecord(state="passed", fingerprint="abc123")
        inp = _default_input(verification=vr, current_fingerprint="abc123")
        assert _verification_current_and_ok(inp) is True


class TestCannotAssess:
    def test_archived_returns_false(self) -> None:
        c = _change(is_archived=True)
        assert _cannot_assess(_default_input(change=c)) is False

    def test_no_diagnostics(self) -> None:
        assert _cannot_assess(_default_input()) is False

    def test_mixed_diagnostics(self) -> None:
        diags = (
            Diagnostic(level=DiagnosticLevel.ERROR, message="fail"),
            Diagnostic(level=DiagnosticLevel.INFO, message="ok"),
        )
        c = _change(artifact_diagnostics=diags)
        assert _cannot_assess(_default_input(change=c)) is False

    def test_all_errors(self) -> None:
        diags = (
            Diagnostic(level=DiagnosticLevel.ERROR, message="fail1"),
            Diagnostic(level=DiagnosticLevel.ERROR, message="fail2"),
        )
        c = _change(artifact_diagnostics=diags)
        assert _cannot_assess(_default_input(change=c)) is True

    def test_all_warnings_not_enough(self) -> None:
        diags = (
            Diagnostic(level=DiagnosticLevel.WARNING, message="warn"),
            Diagnostic(level=DiagnosticLevel.WARNING, message="warn2"),
        )
        c = _change(artifact_diagnostics=diags)
        assert _cannot_assess(_default_input(change=c)) is False


class TestEvaluateBlockers:
    def test_no_metadata(self) -> None:
        c = _change(metadata=None)
        inp = _default_input(change=c)
        base = _draft_assessment(inp)
        assert _evaluate_blockers(inp, base) == ()

    def test_no_blocked_reason(self) -> None:
        meta = ChangeMetadata()
        c = _change(metadata=meta)
        inp = _default_input(change=c)
        base = _draft_assessment(inp)
        assert _evaluate_blockers(inp, base) == ()

    def test_with_blocked_reason(self) -> None:
        meta = ChangeMetadata(blocked_reason="Waiting for dependencies")
        c = _change(metadata=meta)
        inp = _default_input(change=c)
        base = _draft_assessment(inp)
        blockers = _evaluate_blockers(inp, base)
        assert len(blockers) == 1
        assert blockers[0].code == "MANUAL_BLOCK"
        assert blockers[0].message == "Waiting for dependencies"
        assert blockers[0].severity == "warning"


# --- assessment functions ---


class TestArchivedAssessment:
    def test_status_and_reasons(self) -> None:
        a = _archived_assessment(_default_input())
        assert a.status == ChangeStatus.ARCHIVED
        assert "archive directory" in a.reasons[0]
        assert "unarchive" in a.available_actions


class TestUnknownAssessment:
    def test_status_and_actions(self) -> None:
        a = _unknown_assessment(_default_input())
        assert a.status == ChangeStatus.UNKNOWN
        assert "review_artifacts" in a.available_actions

    def test_includes_error_diagnostics(self) -> None:
        diags = (
            Diagnostic(level=DiagnosticLevel.ERROR, message="parse error"),
            Diagnostic(level=DiagnosticLevel.WARNING, message="minor"),
        )
        c = _change(artifact_diagnostics=diags)
        a = _unknown_assessment(_default_input(change=c))
        assert "parse error" in a.warnings
        assert "minor" not in a.warnings


class TestDraftAssessment:
    def test_status(self) -> None:
        a = _draft_assessment(_default_input())
        assert a.status == ChangeStatus.DRAFT
        assert "propose" in a.available_actions


class TestPlanningAssessment:
    def test_missing_artifacts(self) -> None:
        arts = tuple(
            ArtifactInfo(
                kind=k,
                path=Path(f"/fake/{k.value}.md"),
                absolute_path=Path(f"/fake/{k.value}.md"),
                exists=True,
            )
            for k in (ArtifactKind.PROPOSAL,)
        )
        c = _change(artifacts=arts)
        a = _planning_assessment(_default_input(change=c))
        assert a.status == ChangeStatus.PLANNING
        assert any("Missing" in r for r in a.reasons)

    def test_fallback_reason(self) -> None:
        from opsx_tui.domain.change_parser import ParsedTaskList

        pt = ParsedTaskList(
            items=(
                ParsedTaskItem(line_number=1, text="a", checked=False, section=""),
            ),
            total=1,
            completed=0,
            section_map={}, diagnostics=(),
        )
        c = _change(parsed_tasks=pt)
        a = _planning_assessment(_default_input(change=c))
        assert a.status == ChangeStatus.PLANNING
        assert "requires planning" in a.reasons[0]


class TestReadyAssessment:
    def test_status_and_actions(self) -> None:
        a = _ready_assessment(_default_input())
        assert a.status == ChangeStatus.READY
        assert "apply" in a.available_actions


class TestApplyingAssessment:
    def test_with_tasks(self) -> None:
        from opsx_tui.domain.change_parser import ParsedTaskList

        pt = ParsedTaskList(
            items=(
                ParsedTaskItem(line_number=1, text="a", checked=True, section=""),
                ParsedTaskItem(line_number=2, text="b", checked=False, section=""),
            ),
            total=3,
            completed=1,
            section_map={}, diagnostics=(),
        )
        c = _change(parsed_tasks=pt)
        a = _applying_assessment(_default_input(change=c))
        assert a.status == ChangeStatus.APPLYING
        assert "1 of 3" in a.reasons[0]

    def test_without_tasks(self) -> None:
        c = _change(parsed_tasks=None)
        a = _applying_assessment(_default_input(change=c))
        assert a.status == ChangeStatus.APPLYING
        assert "Tasks in progress" in a.reasons[0]


class TestVerificationAssessment:
    def test_no_verification_record(self) -> None:
        a = _verification_assessment(_default_input(verification=None))
        assert a.status == ChangeStatus.VERIFICATION
        assert "verify" in a.available_actions

    def test_stale_verification(self) -> None:
        vr = VerificationRecord(state="passed", fingerprint="old")
        a = _verification_assessment(
            _default_input(verification=vr, current_fingerprint="new")
        )
        assert a.status == ChangeStatus.VERIFICATION
        assert any("stale" in r for r in a.reasons)


class TestReadyToArchiveAssessment:
    def test_status_and_actions(self) -> None:
        a = _ready_to_archive_assessment(_default_input())
        assert a.status == ChangeStatus.READY_TO_ARCHIVE
        assert "archive" in a.available_actions


class TestBlockedAssessment:
    def test_wraps_underlying(self) -> None:
        base = _draft_assessment(_default_input())
        blockers = (BlockingCondition(code="X", message="paused"),)
        a = _blocked_assessment(base, blockers)
        assert a.status == ChangeStatus.BLOCKED
        assert a.underlying_status == ChangeStatus.DRAFT
        assert "Blocked: paused" in a.reasons
        assert a.blocking_conditions == blockers
        assert "unblock" in a.available_actions


# --- assess_lifecycle ---


class TestAssessLifecycle:
    def test_archived(self) -> None:
        c = _change(is_archived=True)
        a = assess_lifecycle(_default_input(change=c))
        assert a.status == ChangeStatus.ARCHIVED

    def test_unknown_all_errors(self) -> None:
        diags = (
            Diagnostic(level=DiagnosticLevel.ERROR, message="fail"),
        )
        c = _change(artifact_diagnostics=diags)
        a = assess_lifecycle(_default_input(change=c))
        assert a.status == ChangeStatus.UNKNOWN

    def test_draft_no_proposal(self) -> None:
        c = _change(parsed_proposal=None)
        a = assess_lifecycle(_default_input(change=c))
        assert a.status == ChangeStatus.DRAFT

    def test_planning_missing_artifacts(self) -> None:
        arts = tuple(
            ArtifactInfo(
                kind=k,
                path=Path(f"/fake/{k.value}.md"),
                absolute_path=Path(f"/fake/{k.value}.md"),
                exists=True,
            )
            for k in (ArtifactKind.PROPOSAL,)
        )
        c = _change(artifacts=arts)
        a = assess_lifecycle(_default_input(change=c))
        assert a.status == ChangeStatus.PLANNING

    def test_ready_no_tasks_completed(self) -> None:
        from opsx_tui.domain.change_parser import ParsedTaskList

        pt = ParsedTaskList(
            items=(ParsedTaskItem(line_number=1, text="x", checked=False, section=""),),
            total=1,
            completed=0,
            section_map={}, diagnostics=(),
        )
        c = _change(parsed_tasks=pt)
        a = assess_lifecycle(_default_input(change=c))
        assert a.status == ChangeStatus.READY

    def test_applying_partial_progress(self) -> None:
        from opsx_tui.domain.change_parser import ParsedTaskList

        pt = ParsedTaskList(
            items=(
                ParsedTaskItem(line_number=1, text="a", checked=True, section=""),
                ParsedTaskItem(line_number=2, text="b", checked=False, section=""),
            ),
            total=2,
            completed=1,
            section_map={}, diagnostics=(),
        )
        c = _change(parsed_tasks=pt)
        a = assess_lifecycle(_default_input(change=c))
        assert a.status == ChangeStatus.APPLYING

    def test_verification_all_done_not_verified(self) -> None:
        from opsx_tui.domain.change_parser import ParsedTaskList

        pt = ParsedTaskList(
            items=(ParsedTaskItem(line_number=1, text="a", checked=True, section=""),),
            total=1,
            completed=1,
            section_map={}, diagnostics=(),
        )
        c = _change(parsed_tasks=pt)
        a = assess_lifecycle(_default_input(change=c, verification=None))
        assert a.status == ChangeStatus.VERIFICATION

    def test_ready_to_archive(self) -> None:
        from opsx_tui.domain.change_parser import ParsedTaskList

        pt = ParsedTaskList(
            items=(ParsedTaskItem(line_number=1, text="a", checked=True, section=""),),
            total=1,
            completed=1,
            section_map={}, diagnostics=(),
        )
        vr = VerificationRecord(state="passed", fingerprint="abc123")
        c = _change(parsed_tasks=pt)
        a = assess_lifecycle(
            _default_input(change=c, verification=vr, current_fingerprint="abc123")
        )
        assert a.status == ChangeStatus.READY_TO_ARCHIVE

    def test_blocked_overrides_ready(self) -> None:
        from opsx_tui.domain.change_parser import ParsedTaskList

        pt = ParsedTaskList(
            items=(ParsedTaskItem(line_number=1, text="x", checked=False, section=""),),
            total=1,
            completed=0,
            section_map={}, diagnostics=(),
        )
        meta = ChangeMetadata(blocked_reason="Waiting for approval")
        c = _change(parsed_tasks=pt, metadata=meta)
        a = assess_lifecycle(_default_input(change=c))
        assert a.status == ChangeStatus.BLOCKED
        assert a.underlying_status == ChangeStatus.READY
        assert a.blocking_conditions[0].code == "MANUAL_BLOCK"

    def test_deterministic_same_input_same_result(self) -> None:
        inp = _default_input()
        a1 = assess_lifecycle(inp)
        a2 = assess_lifecycle(inp)
        assert a1.status == a2.status
        assert a1.reasons == a2.reasons
