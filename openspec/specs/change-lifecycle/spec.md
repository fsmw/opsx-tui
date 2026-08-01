## Purpose

Infer the lifecycle state of each OpenSpec change deterministically from available evidence (artifacts, tasks, verifications, fingerprints, metadata blocks). The inference is a pure domain function producing structured assessments with status, reasons, actions, and warnings.

---

## Requirements

### Requirement: Change status enum with 9 lifecycle states

The system SHALL use a `ChangeStatus` enum with 9 values: `draft`, `planning`, `ready`, `applying`, `verification`, `ready-to-archive`, `blocked`, `archived`, `unknown`.

#### Scenario: Enum contains all 9 states
- **WHEN** the `ChangeStatus` enum is inspected
- **THEN** it SHALL contain exactly: draft, planning, ready, applying, verification, ready-to-archive, blocked, archived, unknown

#### Scenario: Enum is a string enum
- **WHEN** a `ChangeStatus` value is serialized
- **THEN** it SHALL produce its lowercase kebab-case string representation

---

### Requirement: Frozen lifecycle input model

The system SHALL define a `LifecycleInput` frozen Pydantic model with fields: `change`, `required_artifacts`, `verification`, `openspec_state`, `backend_availability`, `git_state`, `current_fingerprint`.

#### Scenario: Required fields are non-optional
- **GIVEN** a `LifecycleInput` instance
- **WHEN** `change` or `required_artifacts` is omitted
- **THEN** construction SHALL raise a validation error

#### Scenario: Deferred fields default to None or empty
- **GIVEN** a `LifecycleInput` constructed with only `change` and `required_artifacts`
- **THEN** `verification` SHALL be `None`
- **AND** `openspec_state` SHALL be `None`
- **AND** `backend_availability` SHALL be `()`
- **AND** `git_state` SHALL be `None`
- **AND** `current_fingerprint` SHALL be `""`

#### Scenario: Model is frozen
- **GIVEN** a `LifecycleInput` instance
- **WHEN** attempting to mutate any field
- **THEN** a `ValidationError` SHALL be raised

---

### Requirement: Frozen lifecycle assessment model

The system SHALL define a `LifecycleAssessment` frozen Pydantic model with fields: `status`, `underlying_status`, `reasons`, `warnings`, `blocking_conditions`, `available_actions`, `assessed_at`, `input_fingerprint`.

#### Scenario: Default blocked state has no underlying status
- **GIVEN** a `LifecycleAssessment` with `status=draft`
- **WHEN** no block exists
- **THEN** `underlying_status` SHALL be `None`
- **AND** `blocking_conditions` SHALL be `()`

#### Scenario: Blocked assessment preserves underlying status
- **GIVEN** a `LifecycleAssessment` with `status=blocked`
- **AND** `underlying_status=applying`
- **WHEN** the assessment is inspected
- **THEN** `blocking_conditions` SHALL contain at least one `BlockingCondition`
- **AND** `underlying_status` SHALL be `applying`

#### Scenario: Assessment includes timestamp
- **GIVEN** a `LifecycleAssessment`
- **WHEN** inspected
- **THEN** `assessed_at` SHALL be a non-None datetime

---

### Requirement: Deterministic lifecycle assessment algorithm

The `assess_lifecycle` function SHALL compute a deterministic `LifecycleAssessment` from a `LifecycleInput` following the precedence: archived, blocked, ready-to-archive, verification, applying, ready, planning, draft, unknown.

#### Scenario: Archived change always returns archived
- **GIVEN** a change with `is_archived=True`
- **WHEN** `assess_lifecycle` is called
- **THEN** `status` SHALL be `archived`
- **REGARDLESS** of artifact availability, task progress, or diagnostics

#### Scenario: Active change with no proposal returns draft
- **GIVEN** an active change with no `proposal.md`
- **WHEN** `assess_lifecycle` is called
- **THEN** `status` SHALL be `draft`

#### Scenario: Active change with proposal but missing required design returns planning
- **GIVEN** an active change with a valid `proposal.md`
- **AND** design is required
- **AND** `design.md` is absent
- **WHEN** `assess_lifecycle` is called
- **THEN** `status` SHALL be `planning`

#### Scenario: Change with all required artifacts and no completed tasks returns ready
- **GIVEN** an active change with proposal, design, and tasks available
- **AND** tasks.md has 5 tasks with 0 completed
- **WHEN** `assess_lifecycle` is called
- **THEN** `status` SHALL be `ready`

#### Scenario: Change with some tasks completed and some pending returns applying
- **GIVEN** an active change with required artifacts
- **AND** 3 of 7 tasks are completed
- **WHEN** `assess_lifecycle` is called
- **THEN** `status` SHALL be `applying`

#### Scenario: Change with all tasks completed and no verification returns verification
- **GIVEN** an active change with required artifacts
- **AND** 10 of 10 tasks are completed
- **AND** no verification record exists
- **WHEN** `assess_lifecycle` is called
- **THEN** `status` SHALL be `verification`

#### Scenario: Change with all tasks completed and current verification returns ready-to-archive
- **GIVEN** an active change with required artifacts
- **AND** all tasks are completed
- **AND** a verification record exists with state `passed`
- **AND** the verified fingerprint matches the current fingerprint
- **WHEN** `assess_lifecycle` is called
- **THEN** `status` SHALL be `ready-to-archive`

#### Scenario: Stale verification returns verification
- **GIVEN** an active change with all tasks completed
- **AND** a verification record exists with state `passed`
- **AND** the verified fingerprint does NOT match the current fingerprint
- **WHEN** `assess_lifecycle` is called
- **THEN** `status` SHALL be `verification`

#### Scenario: Unknown when critical data is missing
- **GIVEN** a change that cannot be safely assessed (e.g., unreadable artifacts, contradictory state)
- **WHEN** `assess_lifecycle` is called
- **THEN** `status` SHALL be `unknown`
- **AND** `reasons` SHALL include a diagnostic message

---

### Requirement: Block detection from manual metadata

When `ChangeMetadata.blocked_reason` is not None, the assessment SHALL return `status=blocked` with `underlying_status` set to the computed methodological state.

#### Scenario: Manual block on an applying change
- **GIVEN** a change with some tasks completed and some pending
- **AND** `metadata.blocked_reason = "Waiting for credentials"`
- **WHEN** `assess_lifecycle` is called
- **THEN** `status` SHALL be `blocked`
- **AND** `underlying_status` SHALL be `applying`
- **AND** `blocking_conditions` SHALL contain a `BlockingCondition` with the reason text

#### Scenario: No block when blocked_reason is None
- **GIVEN** a change with `metadata.blocked_reason = None`
- **WHEN** `assess_lifecycle` is called
- **THEN** `status` SHALL NOT be `blocked` (unless other block sources exist)

---

### Requirement: Available actions per lifecycle state

Each `LifecycleAssessment` SHALL include `available_actions` based on the assessed state.

#### Scenario: Draft state actions
- **GIVEN** a change assessed as `draft`
- **WHEN** the assessment is inspected
- **THEN** `available_actions` SHALL include at minimum: explore, propose

#### Scenario: Ready state actions
- **GIVEN** a change assessed as `ready`
- **WHEN** the assessment is inspected
- **THEN** `available_actions` SHALL include at minimum: apply

#### Scenario: Archived state restricts actions
- **GIVEN** a change assessed as `archived`
- **WHEN** the assessment is inspected
- **THEN** `available_actions` SHALL NOT include: apply, verify, archive

---

### Requirement: Lifecycle assessment is deterministic

For the same `LifecycleInput`, `assess_lifecycle` SHALL return an identical `LifecycleAssessment` every time.

#### Scenario: Repeated calls produce identical results
- **GIVEN** a fixed `LifecycleInput`
- **WHEN** `assess_lifecycle` is called twice
- **THEN** both results SHALL be identical except for `assessed_at`

---

### Requirement: Task progress rules

The assessment SHALL derive progress from `ParsedTaskList.total` and `ParsedTaskList.completed`.

#### Scenario: Empty tasks.md is not ready
- **GIVEN** an active change with all required artifacts
- **AND** tasks.md has 0 total tasks
- **WHEN** `assess_lifecycle` is called
- **THEN** `status` SHALL be `planning`
- **AND** `warnings` SHALL include a note about empty task list

#### Scenario: 100% completed is not applying
- **GIVEN** an active change with all required artifacts
- **AND** 5 of 5 tasks are completed
- **WHEN** `assess_lifecycle` is called
- **THEN** `status` SHALL NOT be `applying`

#### Scenario: 0% completed is not applying
- **GIVEN** an active change with all required artifacts
- **AND** 0 of 5 tasks are completed
- **WHEN** `assess_lifecycle` is called
- **THEN** `status` SHALL NOT be `applying`

---

### Requirement: BlockingCondition model

The system SHALL define a `BlockingCondition` frozen Pydantic model with fields: `code`, `message`, `severity`, `recoverable`, `suggested_actions`.

#### Scenario: BlockingCondition is immutable
- **GIVEN** a `BlockingCondition` instance
- **WHEN** attempting to mutate any field
- **THEN** a `ValidationError` SHALL be raised

#### Scenario: Severity must be a valid diagnostic level
- **GIVEN** a `BlockingCondition` with `severity="warning"`
- **WHEN** the condition is created
- **THEN** it SHALL be valid

---

### Requirement: RequiredArtifact model

The system SHALL define a `RequiredArtifact` frozen Pydantic model with fields: `name` (str), `required` (bool, default True).

#### Scenario: Required artifact with defaults
- **GIVEN** `RequiredArtifact(name="proposal")`
- **WHEN** inspected
- **THEN** `required` SHALL be `True`

#### Scenario: Optional artifact
- **GIVEN** `RequiredArtifact(name="delta_specs", required=False)`
- **WHEN** inspected
- **THEN** `required` SHALL be `False`
