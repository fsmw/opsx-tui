## ADDED Requirements

### Requirement: ChangeStatus replaces ChangeState
The system SHALL define `ChangeStatus` as a `StrEnum` replacing `ChangeState`. The new enum SHALL contain 9 values: `DRAFT`, `PLANNING`, `READY`, `APPLYING`, `VERIFICATION`, `READY_TO_ARCHIVE`, `BLOCKED`, `ARCHIVED`, `UNKNOWN`. The old `ChangeState` enum and `infer_change_state()` function SHALL be removed. Lifecycle assessment SHALL use the new `assess_lifecycle(LifecycleInput) -> LifecycleAssessment` pure function from `domain/lifecycle.py`.

#### Scenario: ChangeStatus values
- **WHEN** the `ChangeStatus` enum is inspected
- **THEN** it SHALL contain exactly: DRAFT, PLANNING, READY, APPLYING, VERIFICATION, READY_TO_ARCHIVE, BLOCKED, ARCHIVED, UNKNOWN

#### Scenario: ChangeState no longer exists
- **WHEN** code imports `from opsx_tui.domain.change_parser import ChangeState`
- **THEN** the import SHALL fail (module no longer exports it)

#### Scenario: inference uses new lifecycle function
- **WHEN** workspace reader processes changes
- **THEN** it SHALL call `LifecycleService.assess()` instead of `infer_change_state()`

## MODIFIED Requirements

### Requirement: Change model extension
The `Change` model SHALL have field `state: ChangeStatus = ChangeStatus.UNKNOWN` (type changed from `ChangeState` to `ChangeStatus`). The model SHALL also have optional fields: `parsed_proposal: ParsedProposal | None = None`, `parsed_design: ParsedDesign | None = None`, `parsed_tasks: ParsedTaskList | None = None`, `artifact_diagnostics: tuple[Diagnostic, ...] = ()`, `metadata: ChangeMetadata | None = None`. Existing code that constructs `Change` without these fields SHALL continue to work.

#### Scenario: Old code creates Change without new fields
- **WHEN** existing code creates `Change(name=..., artifacts=...)` without the new keyword arguments
- **THEN** the Change is created with `state=UNKNOWN` and `parsed_* = None` (backward compatible)

#### Scenario: Change with parsed content
- **WHEN** a Change is created with `state=READY`, `parsed_tasks=...`, `parsed_proposal=...`
- **THEN** all fields are accessible and frozen

### Requirement: Workspace reader integration
The `FilesystemWorkspaceReader` SHALL invoke `LifecycleService.assess()` after scanning and parsing change artifacts, replacing the old `infer_change_state()` call. The `Change.state` field SHALL be populated from the resulting `LifecycleAssessment.status`.

#### Scenario: Workspace scan assesses lifecycle
- **WHEN** `read_workspace()` scans a changes directory
- **THEN** every Change's `state` is set from a lifecycle assessment

#### Scenario: Missing artifact produces planning state
- **WHEN** a change is missing `design.md`
- **THEN** the Change has `state=PLANNING` and `artifact_diagnostics` contains a WARNING

#### Scenario: Unreadable file produces diagnostic
- **WHEN** an artifact file exists but cannot be read
- **THEN** the Change has an ERROR diagnostic in `artifact_diagnostics`

### Requirement: Fixtures for change parsing
The test fixtures SHALL include a valid change directory (all artifacts, well-formed), an incomplete change directory (missing artifacts), and a malformed change directory (artifacts with broken markdown).

#### Scenario: Valid change fixture
- **WHEN** the valid change fixture is parsed
- **THEN** all parsed fields are populated, no diagnostics are produced, and state is READY (or DRAFT/PLANNING depending on artifact completeness)

#### Scenario: Incomplete change fixture
- **WHEN** the incomplete change fixture is scanned
- **THEN** missing artifacts have None parsed content and diagnostics contain WARNINGs; state reflects lifecycle rules (DRAFT or PLANNING)

#### Scenario: Malformed change fixture
- **WHEN** the malformed change fixture is parsed
- **THEN** each artifact's diagnostic contains parsing warnings; state reflects the lifecycle assessment of the malformed content
