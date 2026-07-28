## Why

The workspace catalog (`read-openspec-workspace`) discovers change directories and tells us which artifact files exist (proposal.md, design.md, tasks.md, specs/). But `ArtifactInfo` only carries `kind`, `path`, and `exists` — no content, no structure, no validity. This means the TUI cannot yet show anything useful about a change beyond a file list.

To build change detail screens, a Kanban with states, and lifecycle inference, we need structured content for every change artifact. proposal.md, design.md, and tasks.md follow consistent Markdown conventions across this project — section headings, decision lists, task checkboxes. This change parses them into typed models, infers a basic change state from artifact completeness, and lays the structural foundation for the lifecycle engine and Kanban views.

## What Changes

- Add `ParsedProposal` model (frozen Pydantic) with extracted section headings and body text per section. Detect known sections (`## Why`, `## What Changes`, `## Capabilities`, `## Impact`) and flag unknown/missing sections.
- Add `ParsedDesign` model with extracted sections, decision blocks (numbered items with context + alternatives), and risk/trade-off entries.
- Add `ParsedTaskList` model with task items (checkbox state, text, line number, section group) and completion statistics.
- Add `ChangeState` enum: `UNKNOWN`, `INCOMPLETE`, `PARTIALLY_VALID`, `ACTIVE`, `ARCHIVED`. Inferred from artifact presence + content diagnostics.
- Extend `Change` with `state`, `parsed_proposal`, `parsed_design`, `parsed_tasks`, and `artifact_diagnostics` fields.
- Implement pure parsers in `domain/`: `parse_proposal_markdown()`, `parse_design_markdown()`, `parse_task_markdown()` — line-by-line state machines like `parse_spec_markdown()`.
- Update `FilesystemWorkspaceReader` to read and parse artifact content during workspace scans.
- Add `ChangeParserService` in `application/` orchestrating artifact parsing.
- Add fixtures for valid, incomplete, and malformed change directories.
- Add tests: model invariants, parsing edge cases, state inference rules, writer integration.
- No new external dependencies.
- All models frozen, following existing patterns.

## Capabilities

### New Capabilities
- `change-parsing`: Structured parsing of proposal.md, design.md, and tasks.md; ChangeState inference; artifact diagnostics.

### Modified Capabilities
- `workspace-catalog`: `Change` model gains `state`, parsed artifact fields, and `artifact_diagnostics`.

## Impact

- Domain models: `ParsedProposal`, `ParsedDesign`, `ParsedTaskItem`, `ParsedTaskList`, `ChangeState`.
- Domain parsers: `change_parser.py` with 3 parse functions.
- `workspace.py`: `Change` gains new fields (backward-compatible via Pydantic defaults).
- `workspace_reader.py`: Reader reads + parses artifact content after path detection.
- New fixtures in `tests/fixtures/`: valid change, incomplete change (missing artifacts), malformed change (broken markdown).
- Tests: model tests, parser unit tests for each artifact, state inference tests, integration with workspace reader.
- No API breakage: existing `Change` fields remain; new fields have defaults.