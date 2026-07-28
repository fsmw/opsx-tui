## Purpose

Define models and a pure parser function for extracting requirements, scenarios,
and their metadata from spec Markdown. Consumers (spec browser, change detail)
use the structured models instead of raw text.

## ADDED Requirements

### Requirement: ParsedSpec domain model
The system SHALL define `ParsedSpec(BaseModel, frozen=True)` with fields: `name: str`, `title: str`, `raw_markdown: str`, `requirements: tuple[SpecRequirement, ...]`, `diagnostics: tuple[Diagnostic, ...]`. `SpecRequirement` SHALL have `name: str`, `body: str`, `scenarios: tuple[SpecScenario, ...]`, `line_start: int`, `line_end: int`. `SpecScenario` SHALL have `name: str`, `when_clause: str`, `then_clause: str`, `line_start: int`, `line_end: int`. All models SHALL be `frozen=True`.

#### Scenario: ParsedSpec is frozen
- **WHEN** a `ParsedSpec` is instantiated
- **THEN** attempting to mutate any field raises `ValidationError`

#### Scenario: Requirement with scenarios
- **WHEN** a spec has a requirement with two scenarios
- **THEN** the requirement's `scenarios` tuple has two entries with correct names, WHEN, and THEN clauses

#### Scenario: Scenario without WHEN produces INFO diagnostic
- **WHEN** a `#### Scenario:` header is followed by a THEN clause but no WHEN clause
- **THEN** an `INFO` diagnostic is added and the scenario still contains its name and THEN

#### Scenario: Requirement without scenarios
- **WHEN** a requirement has no `#### Scenario:` blocks
- **THEN** its `scenarios` is an empty tuple

### Requirement: Pure parser function
The system SHALL define `parse_spec_markdown(markdown: str, spec_name: str) -> ParsedSpec` as a pure function in `domain/spec_parser.py`. It SHALL NOT perform I/O. It SHALL use a line-by-line state machine.

#### Scenario: Parse canonical spec
- **WHEN** `parse_spec_markdown` is called with the content of a valid `spec.md`
- **THEN** it returns a `ParsedSpec` with correct name, requirements, and scenarios

#### Scenario: Empty string returns empty spec
- **WHEN** `parse_spec_markdown` is called with an empty string
- **THEN** it returns a `ParsedSpec` with zero requirements and a diagnostic indicating empty content

#### Scenario: Title from directory name
- **WHEN** `parse_spec_markdown` is called with `spec_name="project-foundation"`
- **THEN** the returned `ParsedSpec.title` is `"Project Foundation"`

#### Scenario: Raw markdown preserved verbatim
- **WHEN** a spec is parsed
- **THEN** `ParsedSpec.raw_markdown` matches the input string exactly

### Requirement: Resilience to malformed content
The parser SHALL NOT raise exceptions on malformed content. Malformed blocks SHALL produce diagnostics at the appropriate level (`INFO`, `WARNING`, `ERROR`) and SHOULD be skipped with the rest of the spec intact.

#### Scenario: Corrupt scenario doesn't lose requirement
- **WHEN** a spec has three scenarios and the second is malformed
- **THEN** the requirement still contains the first and third scenarios, and a `WARNING` diagnostic is emitted for the second

#### Scenario: Bad requirement header
- **WHEN** a line starts with `### Requirement:` but has no text after the colon
- **THEN** a `WARNING` diagnostic is emitted and the requirement is created with an empty name

### Requirement: Line numbers on every model
Every `SpecRequirement` and `SpecScenario` SHALL carry 1-indexed `line_start` and `line_end` integers indicating the range in the raw markdown.

#### Scenario: Line numbers accurate
- **WHEN** a requirement starts at line 5 and spans to line 20
- **THEN** `requirement.line_start == 5` and `requirement.line_end == 20`

#### Scenario: Diagnostics include line number
- **WHEN** a diagnostic is emitted for a malformed scenario
- **THEN** the diagnostic message includes the line number of the `#### Scenario:` header

### Requirement: SpecParserService in application
The system SHALL define `SpecParserService` in `application/` with a method `parse_spec(spec: CanonicalSpec) -> ParsedSpec | None`. It SHALL read the file content via `Path.read_text()` and delegate to the pure parser function. If the file cannot be read, it SHALL return `None` and emit a log message.

#### Scenario: Spec parsed via service
- **WHEN** `parse_spec` is called with a valid `CanonicalSpec` whose `spec_file` exists
- **THEN** a `ParsedSpec` is returned with the correct content

#### Scenario: Missing spec_file returns None
- **WHEN** `parse_spec` is called with a `CanonicalSpec` where `spec_file is None`
- **THEN** `None` is returned

### Requirement: CanonicalSpec extended with parsed content
`CanonicalSpec` SHALL gain two optional fields: `raw_markdown: str | None` and `parsed: ParsedSpec | None`. When a workspace scan encounters a `spec.md` file, the reader SHALL read its content and parse it, populating both fields.

#### Scenario: Parsed content available after workspace scan
- **WHEN** a workspace is scanned and a valid `spec.md` exists
- **THEN** the corresponding `CanonicalSpec` has `raw_markdown` and `parsed` populated

#### Scenario: Missing spec_file results in None
- **WHEN** a spec directory exists but has no `spec.md`
- **THEN** the `CanonicalSpec` has `raw_markdown=None` and `parsed=None`

### Requirement: Delta specs also parsed
When the workspace reader scans changes, it SHALL also parse any `spec.md` files found under `changes/<name>/specs/`. These SHALL be stored in `Change.artifacts` with `kind=ArtifactKind.SPECS` and their `CanonicalSpec` equivalents within the change's scope.

#### Scenario: Delta spec parsed
- **WHEN** a change directory contains `specs/spec-parsing/spec.md`
- **THEN** the change's artifacts include one with `kind=SPECS` and parsed content is available

### Requirement: Container wiring
The `Container` SHALL provide `SpecParserService` via a property or factory method. The service SHALL be injectable into consumers.

#### Scenario: Container provides service
- **WHEN** `container.spec_parser_service` is accessed
- **THEN** a `SpecParserService` instance is returned
