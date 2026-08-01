# Tasks: Infer Change Lifecycle

## 1. Domain models — lifecycle types

- [x] 1.1 Create `domain/lifecycle.py` with `ChangeStatus` StrEnum (9 values)
- [x] 1.2 Add `RequiredArtifact` frozen Pydantic model (name, required)
- [x] 1.3 Add `BlockingCondition` frozen Pydantic model (code, message, severity, recoverable, suggested_actions)
- [x] 1.4 Add `VerificationRecord` frozen Pydantic model (state, fingerprint, assessed_at, findings)
- [x] 1.5 Add `LifecycleInput` frozen Pydantic model (change, required_artifacts, verification, openspec_state, backend_availability, git_state, current_fingerprint)
- [x] 1.6 Add `LifecycleAssessment` frozen Pydantic model (status, underlying_status, reasons, warnings, blocking_conditions, available_actions, assessed_at, input_fingerprint)
- [x] 1.7 Export all new types from `domain/__init__.py`

## 2. Pure domain inference function

- [x] 2.1 Implement `assess_lifecycle(data: LifecycleInput) -> LifecycleAssessment` — main entry point
- [x] 2.2 Implement `_archived_assessment()` — returns ARCHIVED with reasons, available actions
- [x] 2.3 Implement `_cannot_assess()` — checks for critical missing data or contradictions
- [x] 2.4 Implement `_unknown_assessment()` — returns UNKNOWN with diagnostics
- [x] 2.5 Implement `_draft_assessment()` — proposal missing or invalid returns DRAFT
- [x] 2.6 Implement `_planning_assessment()` — missing required artifacts or empty tasks returns PLANNING
- [x] 2.7 Implement `_ready_assessment()` — all required artifacts present, 0 tasks completed returns READY
- [x] 2.8 Implement `_applying_assessment()` — some tasks completed, some pending returns APPLYING
- [x] 2.9 Implement `_verification_assessment()` — all tasks completed, no current verification returns VERIFICATION
- [x] 2.10 Implement `_ready_to_archive_assessment()` — verification current and passed returns READY-TO-ARCHIVE
- [x] 2.11 Implement `_evaluate_blockers()` — checks metadata.blocked_reason, returns list of BlockingCondition
- [x] 2.12 Implement `_blocked_assessment()` — wraps underlying state with blocking conditions
- [x] 2.13 Implement `_proposal_missing_or_invalid()` — checks parsed_proposal presence
- [x] 2.14 Implement `_missing_required_artifacts()` — compares change artifacts against required list
- [x] 2.15 Implement `_tasks_empty()` — checks parsed_tasks.total == 0
- [x] 2.16 Implement `_no_tasks_completed()` — checks parsed_tasks.completed == 0
- [x] 2.17 Implement `_some_tasks_pending()` — checks 0 < completed < total
- [x] 2.18 Implement `_verification_current_and_ok()` — checks verification fingerprint match and passed state
- [x] 2.19 Implement `_build_reasons()` — produces tuple of reason strings for current assessment
- [x] 2.20 Implement `_available_actions()` — returns tuple of action names per state

## 3. Remove old ChangeState system

- [x] 3.1 Remove `ChangeState` enum from `domain/change_parser.py`
- [x] 3.2 Remove `infer_change_state()` function from `domain/change_parser.py`
- [x] 3.3 Update `Change.state` field type in `domain/workspace.py` to `ChangeStatus`
- [x] 3.4 Remove old `ChangeState` export from `domain/__init__.py`

## 4. Application layer — LifecycleService

- [x] 4.1 Create `application/lifecycle_service.py` with `LifecycleService` class
- [x] 4.2 Implement `_build_input(change)` — constructs LifecycleInput from available data
- [x] 4.3 Implement `assess(change) -> LifecycleAssessment` — public method calling domain function
- [x] 4.4 Implement `assess_all(changes) -> dict[str, LifecycleAssessment]` — batch assessment
- [x] 4.5 Add logging for each assessment (state, reasons summary)
- [x] 4.6 Export from `application/__init__.py`

## 5. Container and workspace reader wiring

- [x] 5.1 Add `create_lifecycle_service()` factory to `Container`
- [x] 5.2 Update `FilesystemWorkspaceReader._scan_changes` to call `LifecycleService.assess()` instead of `infer_change_state()`
- [x] 5.3 Ensure `Change.state` is populated from `LifecycleAssessment.status` during scan
- [x] 5.4 Ensure `Container.create_workspace_reader()` wires lifecycle service into reader

## 6. Presentation layer — view updates

- [x] 6.1 Update `ChangesView._format_change_item()` state badge to map new 9 states
- [x] 6.2 Update `ChangeDetailPanel` Overview tab to show lifecycle reasons and available actions
- [x] 6.3 Update `ChangesView` sort/filter to work with new `ChangeStatus` values
- [x] 6.4 Update any hardcoded old `ChangeState` references in views

## 7. Fixtures

- [x] 7.1 Create `tests/fixtures/lifecycle/` directory structure (draft-empty, planning-missing-design, ready, applying, verification, ready-to-archive, blocked, archived-incomplete, unknown-structure, stale-verification)
- [x] 7.2 Create fixture data for each lifecycle state (minimal Change objects with appropriate parsed content and metadata)

## 8. Tests

### Unit — domain models
- [x] 8.1 Test `ChangeStatus` enum has all 9 values and is a StrEnum
- [x] 8.2 Test `RequiredArtifact` frozen, default required=True, optional when required=False
- [x] 8.3 Test `BlockingCondition` frozen, all fields accessible
- [x] 8.4 Test `LifecycleInput` frozen, required fields mandatory, deferred fields default to None/empty
- [x] 8.5 Test `LifecycleAssessment` frozen, default state has no underlying_status or blocking conditions

### Unit — inference algorithm
- [x] 8.6 Test draft: active change, no proposal
- [x] 8.7 Test draft: active change, unreadable proposal, no other artifacts
- [x] 8.8 Test planning: active change, proposal present, missing required design
- [x] 8.9 Test planning: active change, all artifacts, tasks.md has 0 total
- [x] 8.10 Test ready: active change, all required artifacts, 0 of 5 completed
- [x] 8.11 Test applying: active change, all required artifacts, 3 of 7 completed
- [x] 8.12 Test verification: active change, all required artifacts, 10 of 10 completed, no verification record
- [x] 8.13 Test ready-to-archive: all tasks completed, verification passed, fingerprint matches
- [x] 8.14 Test verification (stale): all tasks completed, verification passed, fingerprint mismatch
- [x] 8.15 Test archived: is_archived=True always dominates
- [x] 8.16 Test blocked: metadata.blocked_reason is not None, underlying_status preserved
- [x] 8.17 Test unknown: critical data missing or contradictory
- [x] 8.18 Test determinism: same input twice produces identical assessment (except assessed_at)

### Unit — application service
- [x] 8.19 Test `LifecycleService.assess()` returns valid assessment
- [x] 8.20 Test `LifecycleService.assess_all()` returns dict of all changes

### Integration — reader and container
- [x] 8.21 Test workspace reader populates Change.state from lifecycle assessment
- [x] 8.22 Test container creates lifecycle service and wires into reader
- [x] 8.23 Test existing workspace fixtures produce correct new lifecycle states

### Regression — existing tests
- [x] 8.24 Update all test references to old `ChangeState` to use `ChangeStatus`
- [x] 8.25 Update all test assertions on `Change.state` to match new lifecycle states
- [x] 8.26 Ensure all existing test suites pass (full `pytest`)

## 9. Quality verification

- [x] 9.1 Run `ruff check .` — zero issues
- [x] 9.2 Run `mypy src` — zero issues
- [x] 9.3 Run `pytest` — all tests pass (existing + new)
- [x] 9.4 Run `pytest` on Python 3.11 (CI gate)
