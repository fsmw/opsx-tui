## Context

All 12 files under `docs/` and the root `README.md` are written in Spanish. The project's build tooling (pyproject.toml), source code comments, OpenSpec artifacts, and `AGENTS.md` are already in English. The docs represent the normative specification for the product — translating them to English is a prerequisite for further development work, ensuring all contributors can reference the same documents in a shared language.

There is no code to change — this is a pure documentation task. The key constraint is preserving all technical content, diagrams, code blocks, document structure, and section anchors during translation.

## Goals / Non-Goals

**Goals:**
- Translate every Spanish-language markdown file to grammatically correct, technically precise English
- Preserve all ASCII diagrams, code blocks, table structures, and markdown formatting
- Keep section headers (`##`, `###`) stable so anchor links (`docs/01-construction-plan.md#phases`) remain valid
- Remove `docs/README.md` (redundant index, content covered by root `README.md` and the `docs/` directory listing)
- Establish `docs-english` as a main spec capability so future changes can reference the requirement

**Non-Goals:**
- Restructuring docs, reorganizing sections, or changing the document hierarchy
- Changing any technical specification's semantics (the translation MUST NOT alter requirements)
- Adding new diagrams, new content, or new documentation
- Retroactively translating archived change artifacts (already in `openspec/changes/archive/` — those stay as-is)
- Translating code comments in `src/` (already in English)

## Decisions

### D1: File-by-file sequential translation
Each file is translated independently and sequentially. This preserves the existing document structure and allows partial verification — each translated file can be reviewed immediately after translation. No cross-file restructuring.

**Alternatives considered**: Bulk translation with structural refactor (rejected — too risky, conflates translation with reorganization).

### D2: Preserve markdown structure exactly
Headers, code blocks, tables, lists, and diagrams are preserved verbatim except for translated prose. Anchor links remain valid. Code blocks and configuration examples are NOT translated (they are technical content, not prose).

**Alternatives considered**: Full re-format (rejected — would break document IDs used by the codebase).

### D3: Technical terms stay as-is
Spanish technical terms that are standard in the domain (e.g., "OpenSpec", "Textual", "Pydantic", "asyncio") are NOT translated — they are proper nouns or library names. Generic technical terms ("hexagonal architecture", "port", "adapter") ARE translated to their standard English equivalents.

**Alternatives considered**: Full Spanish-to-English glossary (rejected — over-engineering for a one-time task; the context of each term suffices).

### D4: `docs/README.md` removal
`docs/README.md` is a 16-line index listing all doc files. Root `README.md` already covers the same information in its "Documentación" section. After translation, root `README.md` serves as the single entry point. Remove `docs/README.md` rather than translating it.

**Alternatives considered**: Translate + keep (rejected — duplicates content, creates maintenance burden).

### D5: No design decisions for the translated docs themselves
This change does not add new architectural decisions to `docs/09-architecture-decision-records.md`. The translation is a mechanical task — not an architecture change. ADRs remain in Spanish until a future change explicitly updates them (if needed).

**Alternatives considered**: Add an ADR for the English-language policy (rejected — the `docs-english` spec requirement is sufficient; ADRs are for architectural tradeoffs, not language policy).

## Risks / Trade-offs

- **Translation fidelity**: Machine translation may introduce subtle semantic drift. → Mitigation: each file is reviewed for technical accuracy after translation. Critical sections (security model, DoD, lifecycle rules) get extra scrutiny.
- **Stale anchors**: If any codebase references docs by Spanish section titles, those references will break. → Mitigation: search for `docs/` references in `src/` and `AGENTS.md` before finalizing; update any found.
- **Archive artifacts remain Spanish**: ~55 archived change artifacts in `openspec/changes/archive/` stay in Spanish. → Acceptable — archived changes are historical records, not normative docs. New changes use English.
