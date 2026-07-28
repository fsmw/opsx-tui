# Tasks: Translate Docs to English

## 1. Core contracts (critical path)

- [x] 1.1 Translate `docs/05-change-lifecycle-rules.md` (1407 lines) — lifecycle rules, state transitions
- [x] 1.2 Translate `docs/10-definition-of-done.md` (973 lines) — DoD checklist, gates
- [x] 1.3 Translate `docs/07-security-model.md` (1365 lines) — binding security rules

## 2. Architecture and domain

- [x] 2.1 Translate `docs/03-domain-model.md` (1676 lines) — domain model, Pydantic types
- [x] 2.2 Translate `docs/09-architecture-decision-records.md` (1188 lines) — ADRs
- [x] 2.3 Translate `docs/architecture.md` (114 lines) — architecture summary (already English)

## 3. Integration and backend

- [x] 3.1 Translate `docs/04-openspec-integration-contract.md` (1394 lines) — OpenSpec integration
- [x] 3.2 Translate `docs/06-agent-backend-contract.md` (1275 lines) — agent backends
- [x] 3.3 Translate `docs/08-testing-strategy.md` (1436 lines) — testing strategy, CI matrix

## 4. Product overview and plan

- [x] 4.1 Translate `docs/01-construction-plan.md` (2113 lines) — phases and change sequence
- [x] 4.2 Translate `docs/02-product-contract.md` (1369 lines) — product overview, features

## 5. Root files

- [x] 5.1 Translate `README.md` (653 lines) — root README
- [x] 5.2 Remove `docs/README.md` (redundant index) — deleted

## 6. Cross-reference verification

- [x] 6.1 Search `src/` and `AGENTS.md` for broken `docs/` references after translation
- [x] 6.2 Verify all internal doc cross-references (e.g., "see §4.2") still resolve correctly
- [x] 6.3 Verify section anchors (markdown heading IDs) are unchanged

## 7. Quality verification

- [x] 7.1 Run `ruff check .` — zero issues (no code changes expected, verify unchanged)
- [x] 7.2 Run `mypy src` — zero issues (no code changes expected, verify unchanged)
- [x] 7.3 Run `pytest` — all existing tests still pass
- [x] 7.4 Manually review critical sections for translation accuracy: security rules, DoD gates, lifecycle precedence rules
