## 1. Domain models for change artifacts

- [x] 1.1 Create `ParsedProposal` model with `sections: dict[str, str]`, `known_sections: frozenset`, `unknown_sections: list[str]`, `missing_sections: list[str]`, `line_ranges: dict[str, tuple[int, int]]`, `diagnostics: tuple[Diagnostic, ...]`
- [x] 1.2 Create `ParsedDesignSection` model with `name: str`, `body: str`, `line_start: int`, `line_end: int`
- [x] 1.3 Create `ParsedDesignDecision` model with `id: str`, `title: str`, `body: str`, `line_start: int`, `line_end: int`
- [x] 1.4 Create `ParsedDesign` model with `sections: tuple[ParsedDesignSection, ...]`, `decisions: tuple[ParsedDesignDecision, ...]`, `diagnostics: tuple[Diagnostic, ...]`
- [x] 1.5 Create `ParsedTaskItem` model with `text: str`, `checked: bool`, `line_number: int`, `section: str`
- [x] 1.6 Create `ParsedTaskList` model with `items: tuple[ParsedTaskItem, ...]`, `total: int`, `completed: int`, `section_map: dict[str, tuple[int, int]]`, `diagnostics: tuple[Diagnostic, ...]`
- [x] 1.7 Create `ChangeState` StrEnum with UNKNOWN, INCOMPLETE, PARTIALLY_VALID, ACTIVE, ARCHIVED

## 2. Change parser module

- [x] 2.1 Implement `_KNOWN_PROPOSAL_SECTIONS` constant and `_PROPOSAL_SECTION_RE` regex
- [x] 2.2 Implement `parse_proposal_markdown()` — line-by-line state machine extracting ## sections, comparing against known set
- [x] 2.3 Implement `_KNOWN_DESIGN_SECTIONS` constant and `_DESIGN_DECISION_RE` regex (`### D\d+: `)
- [x] 2.4 Implement `parse_design_markdown()` — line-by-line state machine extracting ## sections + ### decision blocks inside ## Decisions
- [x] 2.5 Implement `_TASK_CHECKBOX_RE` regex matching `- [ ]` and `- [x]`/`- [X]`
- [x] 2.6 Implement `parse_task_markdown()` — line-by-line state machine extracting checkbox items under ## sections, counting total/completed

## 3. ChangeState inference function

- [x] 3.1 Implement `infer_change_state(is_archived: bool, has_artifacts: dict[ArtifactKind, bool], artifact_diagnostics: Sequence[Diagnostic]) -> ChangeState` with deterministic rules (D5)

## 4. Change model extension

- [x] 4.1 Add optional fields to `Change`: `state: ChangeState = ChangeState.UNKNOWN`, `parsed_proposal: ParsedProposal | None = None`, `parsed_design: ParsedDesign | None = None`, `parsed_tasks: ParsedTaskList | None = None`, `artifact_diagnostics: tuple[Diagnostic, ...] = ()`

## 5. Application service

- [x] 5.1 Create `ChangeParserService` in `application/change_parser_service.py` with `reparse(change, reader) -> Change` method that reads artifact content and runs all three parsers
- [x] 5.2 Wire `ChangeParserService` in `Container`

## 6. Workspace reader update

- [x] 6.1 Update `_scan_changes` in `FilesystemWorkspaceReader` to read proposal.md, design.md, and tasks.md content and parse them
- [x] 6.2 Attach parsed content and diagnostics to each `Change`; compute `state` via `infer_change_state`
- [x] 6.3 Handle file read errors with ERROR diagnostics (per spec: unreadable file → ERROR)

## 7. Fixtures

- [x] 7.1 Create valid change fixture under `tests/fixtures/`: proposal.md, design.md, tasks.md (well-formed)
- [x] 7.2 Create incomplete change fixture: missing design.md, missing tasks.md
- [x] 7.3 Create malformed change fixture: proposal.md with unknown sections, design.md with no decisions, tasks.md with malformed checkboxes

## 8. Tests

- [x] 8.1 Test ParsedProposal model invariants (frozen, defaults)
- [x] 8.2 Test ParsedDesign + ParsedDesignDecision + ParsedDesignSection model invariants
- [x] 8.3 Test ParsedTaskItem + ParsedTaskList model invariants
- [x] 8.4 Test `parse_proposal_markdown`: standard, empty, unknown sections, missing sections
- [x] 8.5 Test `parse_design_markdown`: standard, no decisions, decision without D\d+
- [x] 8.6 Test `parse_task_markdown`: standard, all done, empty, malformed variants, indented, code-block exclusion
- [x] 8.7 Test `infer_change_state`: all five states with edge cases
- [x] 8.8 Test Change model backward compat (constructing without new fields)
- [x] 8.9 Test workspace reader integration: valid change, incomplete change, malformed change
- [x] 8.10 Test ChangeParserService idempotency

## 9. Documentation

- [x] 9.1 Verify existing tests still pass with Change model extension (backward compat)
- [x] 9.2 Run `ruff check .` and fix issues
- [x] 9.3 Run `mypy src` and fix issues