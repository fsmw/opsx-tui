from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel

from opsx_tui.domain.project import DiagnosticLevel
from opsx_tui.domain.status import ChangeStatus
from opsx_tui.domain.workspace import Change


class RequiredArtifact(BaseModel, frozen=True):
    name: str
    required: bool = True


class BlockingCondition(BaseModel, frozen=True):
    code: str
    message: str
    severity: str = "error"
    recoverable: bool = True
    suggested_actions: tuple[str, ...] = ()


class VerificationRecord(BaseModel, frozen=True):
    state: str
    fingerprint: str
    assessed_at: datetime | None = None
    findings: str | None = None


class LifecycleInput(BaseModel, frozen=True):
    change: Change
    required_artifacts: tuple[RequiredArtifact, ...]
    verification: VerificationRecord | None = None
    openspec_state: str | None = None
    backend_availability: tuple[str, ...] = ()
    git_state: dict[str, str] | None = None
    current_fingerprint: str = ""


class LifecycleAssessment(BaseModel, frozen=True):
    status: ChangeStatus
    underlying_status: ChangeStatus | None = None
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    blocking_conditions: tuple[BlockingCondition, ...] = ()
    available_actions: tuple[str, ...] = ()
    assessed_at: datetime
    input_fingerprint: str


def _proposal_missing_or_invalid(data: LifecycleInput) -> bool:
    return data.change.parsed_proposal is None


def _missing_required_artifacts(data: LifecycleInput) -> bool:
    artifact_names = {a.kind.value for a in data.change.artifacts if a.exists}
    for ra in data.required_artifacts:
        if ra.required and ra.name not in artifact_names:
            return True
    return False


def _tasks_empty(data: LifecycleInput) -> bool:
    if data.change.parsed_tasks is None:
        return True
    return data.change.parsed_tasks.total == 0


def _no_tasks_completed(data: LifecycleInput) -> bool:
    if data.change.parsed_tasks is None:
        return True
    return data.change.parsed_tasks.completed == 0


def _some_tasks_pending(data: LifecycleInput) -> bool:
    if data.change.parsed_tasks is None:
        return False
    pt = data.change.parsed_tasks
    return 0 < pt.completed < pt.total


def _verification_current_and_ok(data: LifecycleInput) -> bool:
    if data.verification is None:
        return False
    if data.verification.state != "passed":
        return False
    if data.verification.fingerprint != data.current_fingerprint:
        return False
    return True


def _cannot_assess(data: LifecycleInput) -> bool:
    if data.change.is_archived:
        return False
    total_diags = len(data.change.artifact_diagnostics)
    error_diags = sum(
        1 for d in data.change.artifact_diagnostics
        if d.level in (DiagnosticLevel.ERROR,)
    )
    if total_diags > 0 and error_diags == total_diags:
        return True
    return False


def _evaluate_blockers(
    data: LifecycleInput, base: LifecycleAssessment
) -> tuple[BlockingCondition, ...]:
    blockers: list[BlockingCondition] = []
    meta = data.change.metadata
    if meta is not None and meta.blocked_reason is not None:
        blockers.append(BlockingCondition(
            code="MANUAL_BLOCK",
            message=meta.blocked_reason,
            severity="warning",
            recoverable=True,
            suggested_actions=("Edit metadata to remove block",),
        ))
    return tuple(blockers)


def _archived_assessment(data: LifecycleInput) -> LifecycleAssessment:
    return LifecycleAssessment(
        status=ChangeStatus.ARCHIVED,
        reasons=("Change is in the archive directory",),
        available_actions=("explore", "unarchive"),
        assessed_at=datetime.now(UTC),
        input_fingerprint=data.current_fingerprint,
    )


def _unknown_assessment(data: LifecycleInput) -> LifecycleAssessment:
    return LifecycleAssessment(
        status=ChangeStatus.UNKNOWN,
        reasons=("Critical data missing or unreadable artifacts",),
        warnings=tuple(
            d.message for d in data.change.artifact_diagnostics
            if d.level in (DiagnosticLevel.ERROR,)
        ),
        available_actions=("explore", "review_artifacts"),
        assessed_at=datetime.now(UTC),
        input_fingerprint=data.current_fingerprint,
    )


def _draft_assessment(data: LifecycleInput) -> LifecycleAssessment:
    return LifecycleAssessment(
        status=ChangeStatus.DRAFT,
        reasons=("Proposal is missing or invalid",),
        available_actions=("explore", "propose"),
        assessed_at=datetime.now(UTC),
        input_fingerprint=data.current_fingerprint,
    )


def _planning_assessment(data: LifecycleInput) -> LifecycleAssessment:
    warnings: list[str] = []
    reasons: list[str] = []

    if _proposal_missing_or_invalid(data):
        reasons.append("Proposal is missing or invalid")
    elif _missing_required_artifacts(data):
        artifact_names = {a.kind.value for a in data.change.artifacts if a.exists}
        missing = [
            ra.name for ra in data.required_artifacts
            if ra.required and ra.name not in artifact_names
        ]
        reasons.append(f"Missing required artifacts: {', '.join(missing)}")
    elif _tasks_empty(data):
        reasons.append("Task list is empty")

    if not reasons:
        reasons.append("Change requires planning")

    return LifecycleAssessment(
        status=ChangeStatus.PLANNING,
        reasons=tuple(reasons),
        warnings=tuple(warnings),
        available_actions=("explore", "continue"),
        assessed_at=datetime.now(UTC),
        input_fingerprint=data.current_fingerprint,
    )


def _ready_assessment(data: LifecycleInput) -> LifecycleAssessment:
    return LifecycleAssessment(
        status=ChangeStatus.READY,
        reasons=("All required artifacts present, no tasks completed yet",),
        available_actions=("explore", "apply"),
        assessed_at=datetime.now(UTC),
        input_fingerprint=data.current_fingerprint,
    )


def _applying_assessment(data: LifecycleInput) -> LifecycleAssessment:
    pt = data.change.parsed_tasks
    if pt is not None:
        reason = f"{pt.completed} of {pt.total} tasks completed"
    else:
        reason = "Tasks in progress"
    return LifecycleAssessment(
        status=ChangeStatus.APPLYING,
        reasons=(reason,),
        available_actions=("explore", "apply", "verify"),
        assessed_at=datetime.now(UTC),
        input_fingerprint=data.current_fingerprint,
    )


def _verification_assessment(data: LifecycleInput) -> LifecycleAssessment:
    reasons = ["All tasks completed, verification needed"]
    if data.verification is not None and data.verification.state == "passed":
        if data.verification.fingerprint != data.current_fingerprint:
            reasons.append(
                "Previous verification is stale (fingerprint has changed)"
            )
    return LifecycleAssessment(
        status=ChangeStatus.VERIFICATION,
        reasons=tuple(reasons),
        available_actions=("explore", "verify"),
        assessed_at=datetime.now(UTC),
        input_fingerprint=data.current_fingerprint,
    )


def _ready_to_archive_assessment(data: LifecycleInput) -> LifecycleAssessment:
    return LifecycleAssessment(
        status=ChangeStatus.READY_TO_ARCHIVE,
        reasons=("All tasks completed and verification is current",),
        available_actions=("explore", "archive"),
        assessed_at=datetime.now(UTC),
        input_fingerprint=data.current_fingerprint,
    )


def _blocked_assessment(
    base: LifecycleAssessment, blockers: tuple[BlockingCondition, ...]
) -> LifecycleAssessment:
    return LifecycleAssessment(
        status=ChangeStatus.BLOCKED,
        underlying_status=base.status,
        reasons=base.reasons + tuple(
            f"Blocked: {b.message}" for b in blockers
        ),
        warnings=base.warnings,
        blocking_conditions=blockers,
        available_actions=(
            "explore",
            "unblock",
        ),
        assessed_at=datetime.now(UTC),
        input_fingerprint=base.input_fingerprint,
    )


def assess_lifecycle(data: LifecycleInput) -> LifecycleAssessment:
    if data.change.is_archived:
        return _archived_assessment(data)

    if _cannot_assess(data):
        base = _unknown_assessment(data)
    elif _proposal_missing_or_invalid(data):
        base = _draft_assessment(data)
    elif _missing_required_artifacts(data):
        base = _planning_assessment(data)
    elif _tasks_empty(data):
        base = _planning_assessment(data)
    elif _no_tasks_completed(data):
        base = _ready_assessment(data)
    elif _some_tasks_pending(data):
        base = _applying_assessment(data)
    elif _verification_current_and_ok(data):
        base = _ready_to_archive_assessment(data)
    else:
        base = _verification_assessment(data)

    blockers = _evaluate_blockers(data, base)
    if blockers:
        return _blocked_assessment(base, blockers)
    return base
