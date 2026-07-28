## ADDED Requirements

### Requirement: Documentation language is English
All project documentation files under `docs/` and the root `README.md` SHALL be written in English.

#### Scenario: All docs files are in English
- **GIVEN** a `docs/` directory with markdown files
- **WHEN** inspecting the content of each `.md` file
- **THEN** all prose sections SHALL be in English
- **AND** code blocks, diagrams, and technical identifiers SHALL be preserved as-is

#### Scenario: README is in English
- **GIVEN** the root `README.md` file
- **WHEN** reading any section of the file
- **THEN** all prose SHALL be in English

### Requirement: Translated docs preserve structure
Translated files SHALL preserve the original markdown structure: headers, code blocks, tables, lists, ASCII diagrams, and formatting SHALL remain unchanged except for translated prose text.

#### Scenario: Code blocks are untouched
- **GIVEN** a doc file containing Python, bash, YAML, or TOML code blocks
- **WHEN** the file is translated
- **THEN** the content of every fenced code block SHALL be identical to the original

#### Scenario: Section headers are preserved
- **GIVEN** a doc file with section headers
- **WHEN** the file is translated
- **THEN** every `##` and `###` header SHALL remain at the same line with equivalent English wording

#### Scenario: ASCII diagrams are preserved
- **GIVEN** a doc file containing ASCII-art diagrams
- **WHEN** the file is translated
- **THEN** every diagram character and layout SHALL be unchanged

### Requirement: Translation preserves technical accuracy
The English translation SHALL preserve all technical specifications, requirements, constraints, and numeric thresholds exactly as stated in the original Spanish text.

#### Scenario: DoD checklist is accurate
- **GIVEN** `docs/10-definition-of-do-end.md` in Spanish containing specific quality gates
- **WHEN** the file is translated to English
- **THEN** every gate, threshold, and test condition SHALL convey the same requirement

#### Scenario: Security rules are accurate
- **GIVEN** `docs/07-security-model.md` in Spanish containing binding security rules
- **WHEN** the file is translated to English
- **THEN** every `MUST NOT`, `SHALL`, and constraint SHALL remain enforceable with the same meaning

### Requirement: Removed redundant docs index
`docs/README.md` SHALL be removed as it duplicates content from the root `README.md`.

#### Scenario: Single entry point
- **GIVEN** the root `README.md` is translated to English
- **WHEN** a contributor looks for documentation
- **THEN** the root `README.md` SHALL serve as the sole entry point and index

#### Scenario: docs/README.md does not exist
- **GIVEN** the translation is complete
- **WHEN** listing files under `docs/`
- **THEN** `README.md` SHALL NOT be present in that directory
