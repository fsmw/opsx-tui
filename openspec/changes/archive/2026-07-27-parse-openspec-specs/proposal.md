## Why

`WorkspaceSnapshot` currently enumerates specs as paths only — it knows a `spec.md` exists and nothing more. Every spec-consuming feature (spec browser, change detail, Kanban) will need to read and interpret spec content. This change adds a deterministic, resilient parser that extracts requirements and scenarios from spec Markdown into structured models, preserving the original text for display.

## What Changes

- Add domain models: `SpecRequirement`, `SpecScenario`, `ParsedSpec` (all `frozen=True`).
- Add `parse_spec_markdown(markdown: str, spec_name: str) -> ParsedSpec` pure function in domain.
- Extend `CanonicalSpec` with `parsed: ParsedSpec | None` and `raw_markdown: str | None`.
- Update `FilesystemWorkspaceReader` to parse `spec.md` during workspace scan (lazy per spec, not blocking collection).
- Add diagnostics for partial parse failures — a corrupt scenario never loses the whole spec.
- Parse both canonical specs (`openspec/specs/<name>/spec.md`) and delta specs (`openspec/changes/<name>/specs/**/spec.md`).
- Tests with real spec.md fixtures, malformed content, edge cases.

## Capabilities

### New Capabilities
- `spec-parsing`: Requirements and scenarios extracted from spec Markdown into structured, line-numbered, frozen models.

### Modified Capabilities
- `workspace-catalog`: `CanonicalSpec` gains `parsed` and `raw_markdown` fields.

## Impact

- New files: `src/opsx_tui/domain/spec_parser.py` (models + parser), `tests/fixtures/spec-parsing/` (sample spec.md variants), tests.
- Modified files: `src/opsx_tui/domain/workspace.py`, `src/opsx_tui/domain/ports.py`, `src/opsx_tui/infrastructure/workspace_reader.py`.
- No new dependencies.
- No behavioral change until consumers use the parsed data.