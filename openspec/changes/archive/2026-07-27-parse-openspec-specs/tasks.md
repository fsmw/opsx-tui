## 1. Domain models (spec_parser.py)

- [x] 1.1 Create `src/opsx_tui/domain/spec_parser.py` with `SpecRequirement`, `SpecScenario`, `ParsedSpec` models (all `frozen=True`)
- [x] 1.2 Add `name_to_title()` helper for converting kebab-case dir names to readable titles
- [x] 1.3 Implement `parse_spec_markdown(markdown: str, spec_name: str) -> ParsedSpec` with line-by-line state machine
- [x] 1.4 Handle `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements` sections
- [x] 1.5 Handle `### Requirement:` header with name extraction
- [x] 1.6 Handle `#### Scenario:` header with name extraction
- [x] 1.7 Extract `- **WHEN**` and `- **THEN**` clauses from scenario bodies
- [x] 1.8 Collect requirement body text between header and next header
- [x] 1.9 Preserve `raw_markdown` verbatim in `ParsedSpec`
- [x] 1.10 Generate diagnostics for malformed sections (missing name, orphan WHEN/THEN, unknown section types, empty content)
- [x] 1.11 Test with real spec.md content (project-foundation, project-discovery, workspace-catalog)

## 2. CanonicalSpec extension

- [x] 2.1 Add `raw_markdown: str | None` and `parsed: ParsedSpec | None` fields to `CanonicalSpec` in `workspace.py`
- [x] 2.2 Update `__init__` to accept new fields with default `None` (maintains backward compat)
- [x] 2.3 Ensure frozen=True still enforced

## 3. SpecParserService

- [x] 3.1 Create `src/opsx_tui/application/spec_parser_service.py` with `SpecParserService`
- [x] 3.2 Implement `parse_spec(spec: CanonicalSpec) -> ParsedSpec | None` — read file, delegate to pure function
- [x] 3.3 Handle file read errors gracefully (return None, log warning)

## 4. WorkspaceReader update

- [x] 4.1 Update `FilesystemWorkspaceReader.read_workspace` to read `spec.md` content during spec scanning
- [x] 4.2 Call `parse_spec_markdown` for each spec and populate `CanonicalSpec.parsed` and `.raw_markdown`
- [x] 4.3 Handle parse failures: add diagnostic, set `parsed=None`, keep `raw_markdown` if readable
- [x] 4.4 Also parse delta specs under `changes/<name>/specs/` and attach to `Change.delta_specs`

## 5. Container wiring

- [x] 5.1 Add `spec_parser_service` property to `Container`
- [x] 5.2 Wire `SpecParserService` for constructor injection

## 6. Fixtures

- [x] 6.1 Create `tests/fixtures/spec-parsing/valid/` with a realistic spec.md (3 requirements, 5 scenarios)
- [x] 6.2 Create `tests/fixtures/spec-parsing/malformed/` with a spec.md containing corrupt scenarios and bad headers
- [x] 6.3 Create `tests/fixtures/spec-parsing/empty/` with empty spec.md
- [x] 6.4 Create `tests/fixtures/spec-parsing/delta/` with a delta spec structure under `changes/<name>/specs/`

## 7. Tests

- [x] 7.1 Test `parse_spec_markdown` with valid spec — requirements, scenarios, line numbers
- [x] 7.2 Test with empty string — empty requirements, diagnostic
- [x] 7.3 Test with malformed scenarios — partial results, diagnostics
- [x] 7.4 Test with missing WHEN clause — INFO diagnostic, scenario still returned
- [x] 7.5 Test with custom spec_name → title conversion
- [x] 7.6 Test `SpecParserService.parse_spec` with a valid fixture spec file
- [x] 7.7 Test with non-existent spec_file → None
- [x] 7.8 Test workspace reader returns specs with `parsed` populated
- [x] 7.9 Test frozen model enforcement
- [x] 7.10 Test delta spec parsing via workspace reader

## 8. Documentation

- [x] 8.1 Update `docs/architecture.md` if needed (spec_parser lives in domain as pure function)
- [x] 8.2 Archive change and sync delta spec to canonical