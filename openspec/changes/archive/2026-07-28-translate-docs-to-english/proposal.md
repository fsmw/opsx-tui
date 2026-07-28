## Why

All project documentation in `docs/` and `README.md` is currently written in Spanish (~15,000 lines across 13 files). The project convention requires English as the documentation language — every OpenSpec artifact, every product contract, every design decision must be accessible to English-speaking contributors and tooling. Translation has been deferred but is now blocking further work since `docs/` provides the normative spec that subsequent changes (lifecycle inference, kanban board, etc.) must conform to.

## What Changes

- Translate all 12 files under `docs/` from Spanish to English, preserving structure, formatting, diagrams, code blocks, and technical precision
- Translate `README.md` from Spanish to English, maintaining all sections, architecture overview, shortcuts, and configuration references
- Remove `docs/README.md` (duplicate index file, content already covered by root `README.md` and `docs/` directory listing)
- No code changes, no API changes, no dependency changes — documentation only

## Capabilities

### New Capabilities
- `docs-english`: Project documentation SHALL be written and maintained in English. All normative docs, product contracts, and architecture decisions use English as the canonical language. Translation preserves all technical content, diagrams, code blocks, and structural anchors.

### Modified Capabilities
None — this change does not alter any existing capability's requirements or behavior.

## Impact

- `docs/*.md` — all 12 files translated (structure and anchors preserved)
- `README.md` — translated to English
- `docs/README.md` — removed (redundant)
- `AGENTS.md` — already in English, no changes needed
- No code, no tests, no dependencies affected
