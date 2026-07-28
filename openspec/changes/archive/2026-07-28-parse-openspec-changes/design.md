## Context

The workspace catalog change (`read-openspec-workspace`) added `ArtifactInfo` with `kind`, `path`, and `exists`. This is sufficient for a file tree but not for a change detail view, Kanban state, or lifecycle inference. The three remaining artifacts — proposal.md, design.md, tasks.md — each have a predictable Markdown structure that can be parsed into typed models.

Proposal.md in this project follows a consistent pattern: `## Why` / `## What Changes` / `## Capabilities` / `## Impact`. Design.md uses `## Context` / `## Goals / Non-Goals` / `## Decisions` (with `### D\d+: Title` sub-sections) / `## Risks / Trade-offs`. Tasks.md uses `- [ ]` / `- [x]` grouped under `##` section headers.

The spec parser (`parse_spec_markdown`) established the pattern: pure function in domain, line-by-line state machine, frozen Pydantic models, diagnostics for ambiguity. This change follows the same pattern for the three change artifacts.

## Goals / Non-Goals

**Goals:**
- Parse proposal.md sections (known + unknown), return section map with line ranges.
- Parse design.md decisions as structured entries (id, title, choice, alternatives).
- Parse tasks.md checkboxes with section grouping, completion stats.
- Infer ChangeState from artifact presence + diagnostics: UNKNOWN, INCOMPLETE, PARTIALLY_VALID, ACTIVE, ARCHIVED.
- Extend Change model with parsed content and state (defaults for backward compat).
- Update workspace reader to parse artifacts during scan.
- Wire ChangeParserService in the Container.
- Fixtures for valid, incomplete, and malformed changes.
- Tests for all parsers, state inference, and workspace reader integration.
- No new dependencies.

**Non-Goals:**
- Lifecycle inference beyond basic state (draft/planning/ready/applying/etc.). That's `infer-change-lifecycle`.
- Semantic understanding of proposal/design content (e.g., extracting specific goals from text).
- Markdown rendering or TUI display.
- Editing or writing artifacts.
- Parsing .openspec.yaml or other metadata files.

## Decisions

### D1: All three parsers in one domain module
**Choice:** `domain/change_parser.py` containing `parse_proposal_markdown()`, `parse_design_markdown()`, `parse_task_markdown()` — one module, three functions.
**Why:** They share diagnostic models and the line-by-line pattern. A single module is cohesive; the spec parser is already a single module.
**Alternatives:** One module per artifact — rejected as over-split for three small parsers.

### D2: Proposal parsed by ##-section only
**Choice:** Extract all `## Section Title` blocks as key-value pairs (heading text → body). Maintain a known set of expected sections. Flag unknown sections as WARNING and missing expected sections as WARNING.
**Why:** proposal.md is free-form prose under standard headings. Deep semantic parsing (e.g., parsing "What Changes" into a file list) would be fragile and version-dependent. Section detection is sufficient to validate structure.
**Alternatives:** Regex-based extraction of specific content (e.g., file paths) — rejected as too brittle across proposal variations.

### D3: Design parsed with decision block detection
**Choice:** Detect `### D\d+: Title` blocks inside `## Decisions`. Each block body is captured as raw text. No attempt to parse sub-structure (choice/alternatives/rationale) from prose.
**Why:** Decisions follow `###` heading convention. The body format varies across authors. Raw body + line range is enough for display and validation.
**Alternatives:** Structured parsing of each decision's choice/alternatives/rationale — rejected as too fragile; design.md content conventions are not as strict as spec.md.

### D4: Tasks parsed as flat list with section grouping
**Choice:** `ParsedTaskItem` with fields: `text`, `checked` (bool), `line_number`, `section` (str — parent ## heading). `ParsedTaskList` with: `items`, `total`, `completed`, `section_map`. Support `- [ ]`, `- [x]`, `- [X]`. Nested indentation is tracked but flattened for counting.
**Why:** Matches the construction plan's task tracking spec. Section grouping is essential for progress per group.
**Alternatives:** Nested tree model — rejected; the CLI/display needs flat iteration, and spec tracking is always flat.

### D5: ChangeState inference rules
**Choice:** Deterministic rules applied after parsing:
- `ARCHIVED`: change is under `archive/` directory (from `is_archived`).
- `UNKNOWN`: change dir exists but has no recognized artifacts.
- `INCOMPLETE`: missing one or more required artifacts (proposal, design, tasks, specs dir). Diagnostics have ERROR or WARNING.
- `PARTIALLY_VALID`: all artifacts exist but one or more have content diagnostics.
- `ACTIVE`: all artifacts exist and no content diagnostics.
**Why:** Rule-based, deterministic, verifiable. No machine learning or heuristics.
**Alternatives:** State machine with transitions — rejected; that's lifecycle inference, not basic state.

### D6: Parsed content attached to Change model
**Choice:** Add `parsed_proposal`, `parsed_design`, `parsed_tasks` as `| None` fields on `Change`. Add `state: ChangeState = ChangeState.UNKNOWN` and `artifact_diagnostics: tuple[Diagnostic, ...] = ()`.
**Why:** Consumer code (screens, services) accesses parsed content directly on the Change object without an extra lookup.
**Alternatives:** Separate registry (`change_id -> parsed_content`) — rejected as unnecessary indirection.

### D7: Lazy parsing (upgrade from eager)
**Choice:** The workspace reader parses ALL artifacts during `_scan_changes()`, same pattern as `_scan_specs()` already does.
**Why:** Consistency with existing pattern. Parsing is fast (three small files). Workspace snapshot is the complete truth with no deferred work.
**Alternatives:** Deferred parsing on first access — rejected; inconsistent with spec parsing pattern.

### D8: Same Diagnostic model for artifact diagnostics
**Choice:** Reuse `Diagnostic` from `domain/project.py`. No new diagnostic types.
**Why:** Already has `level` (INFO/WARNING/ERROR) and `message`. Suitable for any parsing diagnostic.
**Alternatives:** New `ArtifactDiagnostic` model — rejected as YAGNI.

## Risks / Trade-offs

- **[Risk] Proposal/design format drift** → If these files change their heading conventions, parsers silently produce empty sections. Mitigation: diagnostics flag unknown sections, so drift is visible.
- **[Trade-off] Task checkbox in code blocks** → Parsers don't recurse into fenced code blocks. Tasks inside ``` blocks will be falsely detected. Acceptable: tasks in code blocks are rare and the consequence is a harmless false match.
- **[Risk] Large task lists** → A change with hundreds of tasks could slow the workspace scan. Mitigation: tasks.md is typically under 100 lines; parsing is O(n) with negligible cost.