## Context

The current `ChangeState` enum and `infer_change_state()` function (`domain/change_parser.py`) produce 5 coarse states from artifact presence only. The lifecycle rules document (`docs/05-change-lifecycle-rules.md`) defines a complete 9-state model with precedence, blocks, progress, verification staleness, and explainable assessments. This change replaces the old system with a deterministic inference engine that can power a Kanban board.

Hexagonal constraints: the inference itself is a pure domain function; an application service wires inputs and orchestrates callers. No presentation layer code changes lifecycle state.

## Goals / Non-Goals

**Goals:**
- Replace `ChangeState` (5 states) with `ChangeStatus` (9 states) as the single lifecycle type
- Implement `assess_lifecycle(LifecycleInput) -> LifecycleAssessment` as a pure domain function
- Support block detection (manual via metadata, future: git, backend, CLI)
- Support verification staleness via fingerprint comparison
- Produce explainable reasons, warnings, and available actions per state
- Wire through application layer, workspace reader, and container

**Non-Goals:**
- Do NOT implement verification records, Git inspection, or CLI state queries (deferred inputs)
- Do NOT implement Kanban board UI (separate change: `add-kanban-board`)
- Do NOT persist lifecycle state in any store (it is always derived)
- Do NOT add new external dependencies

## Decisions

### D1: Replace old `ChangeState` entirely, do not coexist

The old `ChangeState` (UNKNOWN, INCOMPLETE, PARTIALLY_VALID, ACTIVE, ARCHIVED) is replaced by `ChangeStatus` (draft, planning, ready, applying, verification, ready-to-archive, blocked, archived, unknown). The `Change.state` field type changes from `ChangeState` to `ChangeStatus`. All references in code and tests are updated.

**Rationale**: Coexisting two state enums creates confusion. The old states map approximately to the new ones but lose precision — keeping both adds no value. One clean breaking change.

### D2: Pure domain function in `domain/lifecycle.py`

The assessment algorithm is a pure function `assess_lifecycle(data: LifecycleInput) -> LifecycleAssessment` with no side effects, no I/O, and no framework imports. This keeps it deterministic and testable.

```python
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
```

**Rationale**: The pseudocode in `docs/05-change-lifecycle-rules.md` §16 is the authoritative algorithm. A pure function with private helpers is the most testable, reviewable structure.

### D3: Frozen Pydantic models for all domain types

All new models (`ChangeStatus`, `LifecycleInput`, `LifecycleAssessment`, `BlockingCondition`, `RequiredArtifact`) are frozen Pydantic models. This follows the existing project convention (all domain models are `frozen=True`).

**Rationale**: Immutability guarantees determinism — the same input always produces the same assessment.

### D4: `LifecycleInput` with optional deferred fields

Fields not yet available from other subsystems default to `None` and do not block inference:

```python
class LifecycleInput(BaseModel, frozen=True):
    change: Change
    required_artifacts: tuple[RequiredArtifact, ...]
    verification: VerificationRecord | None = None          # deferred
    openspec_state: str | None = None                       # deferred
    backend_availability: tuple[str, ...] = ()              # deferred
    git_state: dict[str, str] | None = None                 # deferred
    current_fingerprint: str = ""
```

**Rationale**: The engine runs now with available data and gracefully degrades. When future changes add verification/CLI/git, the same function accepts richer input without modification.

### D5: Block detection — manual only for now

Blocks are detected from `ChangeMetadata.blocked_reason`. A non-None `blocked_reason` produces a BLOCKED assessment wrapping the computed underlying state. Future block sources (Git conflicts, backend missing, CLI report) will add to `_evaluate_blockers()` without changing the assessment algorithm.

**Rationale**: The block model (`BlockingCondition` with code/message/severity/recoverable/suggested actions) supports manual blocks immediately and technical blocks later.

### D6: Required artifacts — hardcoded for spec-driven schema

`RequiredArtifact` model captures artifact expectations:

```python
class RequiredArtifact(BaseModel, frozen=True):
    name: str
    required: bool = True
```

Default for spec-driven: proposal (required), design (required), tasks (required), delta specs (optional). The `required_artifacts` tuple is passed as input, making the function schema-agnostic.

**Rationale**: Future schemas may have different requirements. The function accepts any artifact list; the caller (service) decides which schema's rules to apply.

### D7: `LifecycleService` in application layer

The application service wires inputs from the current workspace snapshot, calls the pure domain function, and logs the result. It does NOT perform inference itself.

```python
class LifecycleService:
    def assess(self, change: Change) -> LifecycleAssessment:
        input_data = self._build_input(change)
        return assess_lifecycle(input_data)
```

**Rationale**: Separation of concerns — domain function is pure, service handles wiring and logging.

### D8: No new dependencies

The change uses only existing project dependencies (Pydantic, enum, datetime). No new packages required.

**Alternatives considered**: Using `enum` stdlib vs Pydantic `Enum` — Pydantic integrates better with frozen models. Using `datetime` for `assessed_at` timestamp — lightweight, no external dep.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Breaking change on `Change.state` type breaks all existing tests and views | Tests are updated as part of implementation; views re-map to new states |
| Deferred fields (verification, git) may change the API shape later | `LifecycleInput` uses optional fields with defaults; adding new fields is non-breaking |
| 9 states may not map cleanly to the 5-option `ChangeState` labels in views | View badges update to new enum; no semantic conflict since old states were unused in UI |
| `assess_lifecycle` must be deterministic with same inputs | Pure function with frozen inputs guarantees this; property-based tests verify |
