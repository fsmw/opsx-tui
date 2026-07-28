## Context

`WorkspaceSnapshot` currently returns `CanonicalSpec` with paths only. The next two changes (`parse-openspec-specs`, then `parse-openspec-tasks`) add content-level parsing. This change focuses on spec Markdown, which has a consistent structure: `## ADDED/MODIFIED/REMOVED`, `### Requirement:`, `#### Scenario:`, `- **WHEN**`, `- **THEN**`.

Following the established pattern of pure domain logic: the parser is a function `str → ParsedSpec`, no I/O, no protocol needed.

## Goals / Non-Goals

**Goals:**
- Domain models for parsed spec content (all `frozen=True`).
- `parse_spec_markdown()` pure function — line-by-line state machine.
- Title from directory name converted to readable form (e.g. `"project-foundation"` → `"Project Foundation"`).
- Parse both canonical specs (`openspec/specs/<cap>/spec.md`) and delta specs (`openspec/changes/<change>/specs/**/spec.md`).
- Partial parse resilience: a corrupt scenario produces a `WARNING` diagnostic but does not lose the surrounding requirement or spec.
- Original markdown preserved verbatim in `ParsedSpec.raw_markdown`.
- Extend `CanonicalSpec` with `parsed: ParsedSpec | None` and `raw_markdown: str | None`.
- Update `FilesystemWorkspaceReader` to populate these fields lazily (parse spec on demand when accessed, not blocking the workspace scan).
- Diagnostics for: unparseable sections, orphan WHEN/THEN, missing `- **WHEN**` or `- **THEN**` inside a scenario.
- `SpecParserService` in application/ wrapping the function for injection.
- Updated `Container` to wire the service.

**Non-Goals:**
- `tasks.md` parsing (separate change `parse-openspec-tasks`).
- UI for viewing parsed specs (Fase 2 `add-spec-browser`).
- Writing/editing specs.
- Parsing arbitrary Markdown — only the OPSX spec format.
- Caching parsed results beyond the workspace snapshot lifecycle.

## Decisions

### D1: Pure function, not port/adapter
**Choice:** `parse_spec_markdown(markdown: str, spec_name: str) -> ParsedSpec` lives in `domain/spec_parser.py`. No Protocol, no infrastructure adapter.
**Why:** Deterministic text transformation with no I/O — the definition of domain logic. Tests can call it with string literals. A port would add indirection for zero benefit.
**Alternatives:** Port in domain + adapter in infrastructure — rejected as over-engineering for a pure function.

### D2: Line-by-line state machine, not regex-on-whole-text
**Choice:** The parser iterates over `markdown.split("\n")` with a state machine tracking the current section (`ADDED/MODIFIED/REMOVED`), current requirement, and current scenario. Line numbers are tracked.
**Why:** Need accurate line numbers for diagnostics and error reporting. Regex-on-whole-text loses line fidelity.
**Alternatives:** Regex — rejected because line-number tracking becomes imprecise for multi-line bodies.

### D3: Three states tracked: section → requirement → scenario
**Choice:** State enum: `IDLE`, `IN_REQUIREMENT` (collecting body), `IN_SCENARIO` (collecting WHEN/THEN). Section changes (`## ADDED/MODIFIED/REMOVED`) reset the requirement context. A new `### Requirement:` finalizes the current scenario+requirement (if any) and starts a new one.
**Why:** Natural hierarchical structure maps to the parser flow. Scenarios belong to requirements, requirements belong to sections.
**Alternatives:** Flat list — rejected as losing structure; consumers need the hierarchy for spec browsing.

### D4: `SpecParserService` in application
**Choice:** `SpecParserService` wraps the pure function for injection. Takes a `Path` and returns `ParsedSpec | None`. Uses `WorkspaceReader` internally to read the file content, then delegates to the pure function.
**Why:** Application layer handles the I/O (reading the file via reader) while keeping the parser itself pure. Services with real I/O go in application, not infrastructure, when they orchestrate between a port and a pure function.
**Alternatives:** Put the file-read in infrastructure as a `SpecReader` adapter — rejected because it would be a thin wrapper around `Path.read_text()` with no behavioral logic.

### D5: Eager population on workspace scan, but parse happens on demand
**Choice:** `FilesystemWorkspaceReader` stores `raw_markdown` (read from file) and calls `parse_spec_markdown` for each spec during `read_workspace`. The parse result is stored in `CanonicalSpec.parsed`.
**Why:** Workspace scan is already I/O-bound (reading directory listings, checking mtimes). Adding spec.md reads and parsing adds negligible time (spec files are small). This simplifies consumers — they always have parsed data available without lazy-loading infrastructure.
**Alternatives:** Fully lazy parsing — rejected as adding complexity for marginal perf gain.

### D6: Resilience via try/except per scenario
**Choice:** Each `#### Scenario:` block is parsed independently. If a scenario is malformed (e.g., no WHEN clause), a `WARNING` diagnostic is added for that scenario, and parsing continues with the next block. The surrounding requirement is unaffected. If a `### Requirement:` header is followed by unparseable content, an `ERROR` diagnostic is added but the requirement entry still exists with empty body.
**Why:** Follows the rule "Un archivo parcialmente inválido no debe hacer desaparecer toda la spec."
**Alternatives:** Fail-stop — rejected as too brittle for real-world spec files that may have human-authored inconsistencies.

### D7: Line numbers on every model
**Choice:** `SpecRequirement` has `line_start: int`, `line_end: int`. `SpecScenario` has `line_start: int`, `line_end: int`. `ParsedSpec.diagnostics` includes line numbers.
**Why:** The user spec explicitly requires "líneas de origen". Critical for navigating to the source file.
**Alternatives:** Only diagnostics have line numbers — rejected; lacking requirement/scenario bounds makes source mapping imprecise.

### D8: No new dependencies
**Choice:** Use stdlib string parsing only. No `mistune`, `markdown-it-py`, or other Markdown libraries.
**Why:** The spec format is simple enough for a 100-line state machine. An external parser would need configuration to understand our custom semantics anyway.
**Alternatives:** `mistune` for base Markdown parsing + custom renderer — rejected as heavier and no real benefit.

### D9: Canonical + delta specs share the same parser
**Choice:** `parse_spec_markdown` is format-agnostic — it parses any spec.md content regardless of location. The caller (`SpecParserService`) decides which specs to parse: all `CanonicalSpec` entries from the workspace reader, including those inside changes.
**Why:** The spec.md format is identical for canonical and delta specs. Reusing the function avoids duplication.
**Alternatives:** Two parsers — rejected as unnecessary.

## Risks / Trade-offs

- **[Risk] Spec format evolves** → If OpenSpec adds new section types (e.g., `## REMOVED Requirements`), the parser handles gracefully — unknown sections produce `INFO` diagnostics but don't break.
- **[Risk] Very long spec files** → The workspace scan reads every spec.md into memory. With typical files <200 lines, this is negligible. Monitor if specs grow large; add streaming if needed.
- **[Trade-off] Line numbering from raw markdown** → The parser uses 1-indexed lines from the raw markdown string. If the file has mixed line endings, Python handles `\n` split correctly but `\r\n` produces empty trailing `\r`. Accepted — spec files use Unix line endings.
- **[Trade-off] Requirement body captures lines between header and next header** → Body text includes empty lines. This is intentional: consumers may want to display the full description.