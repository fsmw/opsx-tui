## ADDED Requirements

### Requirement: Proposal.md parser
The system SHALL provide a `parse_proposal_markdown(markdown: str) -> ParsedProposal` pure function in `domain/change_parser.py`. It SHALL extract all `## Section Title` blocks as section name → body pairs. It SHALL distinguish known sections (`Why`, `What Changes`, `Capabilities`, `Impact`) from unknown sections and report diagnostics for both missing expected sections and unexpected sections.

#### Scenario: Standard proposal parsed
- **WHEN** a proposal.md with `## Why`, `## What Changes`, `## Capabilities`, and `## Impact` sections is parsed
- **THEN** all four sections are extracted with their body text and no diagnostics are produced

#### Scenario: Unknown section flagged
- **WHEN** a proposal.md contains `## Unusual Section` in addition to known sections
- **THEN** the parsed result includes a WARNING diagnostic for the unexpected section

#### Scenario: Missing section flagged
- **WHEN** a proposal.md is missing `## Impact`
- **THEN** the parsed result includes a WARNING diagnostic for the missing section

#### Scenario: Empty proposal
- **WHEN** an empty string is parsed
- **THEN** `ParsedProposal` has empty sections and an INFO diagnostic

### Requirement: Design.md parser
The system SHALL provide a `parse_design_markdown(markdown: str) -> ParsedDesign` pure function. It SHALL extract `## Section` blocks and `### D\d+: Title` decision blocks inside `## Decisions`. It SHALL capture decision body as raw text with line numbers.

#### Scenario: Design with decisions parsed
- **WHEN** a design.md with `## Context`, `## Decisions` (containing `### D1: Use X` and `### D2: Use Y`), and `## Risks / Trade-offs` is parsed
- **THEN** both decisions are extracted with their names, bodies, and line ranges; sections are extracted

#### Scenario: Decision without number
- **WHEN** a `###` heading inside `## Decisions` does not match `D\d+:` pattern
- **THEN** a WARNING diagnostic is emitted but the block is still captured as a decision with empty id

#### Scenario: Design with no decisions
- **WHEN** a design.md has `## Decisions` but no `###` sub-headings
- **THEN** `ParsedDesign.decisions` is empty and an INFO diagnostic indicates no decisions found

### Requirement: Tasks.md parser
The system SHALL provide a `parse_task_markdown(markdown: str) -> ParsedTaskList` pure function. It SHALL extract `- [ ]` and `- [x]`/`- [X]` items, group them by parent `##` section, and compute `total` and `completed` counts. It SHALL track line numbers. Nested indentation within the same section SHALL be included in `section` but the list is flat.

#### Scenario: Standard task list parsed
- **WHEN** a tasks.md with two `##` sections containing a mix of checked and unchecked items is parsed
- **THEN** all items are extracted with correct `checked` state, `section` assignment, and line numbers; totals match

#### Scenario: All tasks completed
- **WHEN** every `- [ ]` has been changed to `- [x]`
- **THEN** `completed == total` and `progress == 1.0`

#### Scenario: No tasks
- **WHEN** tasks.md has no `- [ ]` or `- [x]` items
- **THEN** `ParsedTaskList.items` is empty, `total == 0`, `completed == 0`

#### Scenario: Malformed checkbox variants
- **WHEN** a line contains `-[ ]` (no space) or `- [X]` (uppercase x) or `* [ ]` (asterisk instead of dash) or `  - [ ]` (indented)
- **THEN** `- [X]` is parsed as checked; `-[ ]` and `* [ ]` are ignored; indented `  - [ ]` is parsed as a valid item with the indentation preserved in text

#### Scenario: Empty tasks file
- **WHEN** an empty string is parsed
- **THEN** `ParsedTaskList` is empty with total=0

### Requirement: ChangeState enum
The system SHALL define `ChangeState` as a `StrEnum` with values `UNKNOWN`, `INCOMPLETE`, `PARTIALLY_VALID`, `ACTIVE`, `ARCHIVED`. Inference SHALL be deterministic from artifact presence and diagnostics.

#### Scenario: Archived change has archived state
- **WHEN** `is_archived=True` is passed to the state inference function
- **THEN** the inferred state is `ARCHIVED`, regardless of artifact content

#### Scenario: No artifacts → UNKNOWN
- **WHEN** a change directory exists but has no recognized artifact files
- **THEN** the inferred state is `UNKNOWN`

#### Scenario: Missing required artifact → INCOMPLETE
- **WHEN** a change has no `proposal.md` or no `tasks.md`
- **THEN** the inferred state is `INCOMPLETE`

#### Scenario: All artifacts exist with content diagnostics → PARTIALLY_VALID
- **WHEN** a change has all required artifacts but one has a WARNING diagnostic (e.g., missing section)
- **THEN** the inferred state is `PARTIALLY_VALID`

#### Scenario: All artifacts exist clean → ACTIVE
- **WHEN** a change has all required artifacts and no parsing diagnostics
- **THEN** the inferred state is `ACTIVE`

### Requirement: Change model extension
The `Change` model SHALL gain optional fields: `state: ChangeState = ChangeState.UNKNOWN`, `parsed_proposal: ParsedProposal | None = None`, `parsed_design: ParsedDesign | None = None`, `parsed_tasks: ParsedTaskList | None = None`, `artifact_diagnostics: tuple[Diagnostic, ...] = ()`. Existing code that constructs `Change` without these fields SHALL continue to work.

#### Scenario: Old code creates Change without new fields
- **WHEN** existing code creates `Change(name=..., artifacts=...)` without the new keyword arguments
- **THEN** the Change is created with `state=UNKNOWN` and `parsed_* = None` (backward compatible)

#### Scenario: Change with parsed content
- **WHEN** a Change is created with `state=ACTIVE`, `parsed_tasks=...`, `parsed_proposal=...`
- **THEN** all fields are accessible and frozen

### Requirement: Workspace reader integration
The `FilesystemWorkspaceReader` SHALL read and parse proposal.md, design.md, and tasks.md content during `_scan_changes`, attaching parsed content and diagnostics to each `Change`. Missing artifacts SHALL have `None` parsed content with a WARNING diagnostic. File read errors SHALL produce ERROR diagnostics.

#### Scenario: Workspace scan parses all artifacts
- **WHEN** `read_workspace()` scans a changes directory
- **THEN** every Change's parsed_* fields are populated from file content when files exist

#### Scenario: Missing artifact produces diagnostic
- **WHEN** a change is missing `design.md`
- **THEN** the Change has `parsed_design=None` and `artifact_diagnostics` contains a WARNING for the missing file

#### Scenario: Unreadable file produces ERROR
- **WHEN** an artifact file exists but cannot be read (e.g., permission denied)
- **THEN** the Change has an ERROR diagnostic in `artifact_diagnostics`

### Requirement: ChangeParserService
The application layer SHALL provide `ChangeParserService` orchestrating the three parsers. Given a `Change` and a `WorkspaceReader`, it SHALL parse all artifact content and return an updated `Change` with parsed fields. This SHALL be idempotent (re-parsing the same content produces the same result).

#### Scenario: Service re-parses change
- **WHEN** `ChangeParserService.reparse(change, reader)` is called
- **THEN** the returned Change has updated parsed_* fields from current file content

#### Scenario: Idempotent parsing
- **WHEN** `reparse()` is called twice on the same change without file changes
- **THEN** the second result matches the first exactly

### Requirement: Fixtures for change parsing
The test fixtures SHALL include a valid change directory (all artifacts, well-formed), an incomplete change directory (missing artifacts), and a malformed change directory (artifacts with broken markdown).

#### Scenario: Valid change fixture
- **WHEN** the valid change fixture is parsed
- **THEN** all parsed fields are populated, no diagnostics are produced, and state is ACTIVE

#### Scenario: Incomplete change fixture
- **WHEN** the incomplete change fixture is scanned
- **THEN** missing artifacts have None parsed content and diagnostics contain WARNINGs; state is INCOMPLETE

#### Scenario: Malformed change fixture
- **WHEN** the malformed change fixture is parsed
- **THEN** each artifact's diagnostic contains parsing warnings; state is PARTIALLY_VALID