# AGENTS.md — OPSX TUI

Guidance for OpenCode agents working in this repo. Read alongside `README.md` and `docs/` — those are normative, this file is the shortcut.

## Project state

Pre-implementation. No `pyproject.toml`, `src/`, or `tests/` exist yet. The README and `docs/01–10-*.md` define the product, architecture, lifecycle, security, testing, and DoD. Treat them as the spec, not as prose to ignore.

The project is built incrementally via OpenSpec changes. See `openspec/` and the `/opsx:*` skills (explore → propose → apply → verify → archive). Every capability ships as one change that must pass the Definition of Done before archiving.

## Stack (planned)

Python 3.11–3.14 (3.11 is the mandatory CI gate, never skip it). Textual (TUI), Pydantic 2, asyncio, watchfiles, TOML config, SQLite, keyring/env for secrets. Tooling: Ruff, MyPy, Pytest + pytest-asyncio + Hypothesis.

Once `pyproject.toml` exists, dev install: `python -m pip install -e ".[dev]"`. Run command: `opsx-tui` (or `opsx-tui --project <path>`, or `OPSX_TUI_PROJECT=<path> opsx-tui`).

## Architecture (enforced)

Hexagonal, four layers — dependencies point inward only:

- `presentation/` — Textual screens/widgets. MUST NOT touch filesystem or subprocesses.
- `application/` — use cases, services, lifecycle rules.
- `domain/` — Pydantic models, rules, contracts. MUST NOT import Textual.
- `infrastructure/` — filesystem, CLI, Git, SQLite, agent adapters. Implements ports.

Hard rules: no `shell=True`, no secrets in TOML/SQLite, no writes outside workspace without auth, no archive with stale verify, no duplicating OpenSpec canonical data into SQLite, no domain logic inside widgets.

## OpenSpec is the source of truth

`openspec/` holds specs, proposals, designs, tasks, delta specs, changes. OPSX TUI only stores operational metadata (config, history, logs, filters) — never re-encodes OpenSpec content as canonical.

Three integration layers, do not conflate: filesystem (persistent content) vs `openspec <cmd>` CLI (state/validation/official commands) vs `/opsx:<action>` agent actions (assisted work via configured backend).

## Development workflow

1. Read the relevant `docs/` contract + existing specs before implementing.
2. Work only within the active change's scope — no scope creep, no silent architecture changes, no new major deps without an ADR.
3. Implement, then run gates in order: `ruff check .` → `mypy src` → `pytest`.
4. Run `/opsx:verify`; archive only if DoD is met and verify is current.
5. Close-report format is fixed (see README §"Rules for agents" / docs/10 §29). Use it; never report just "Terminado."

## Testing constraints

- No test uses the real home dir, real credentials, real Codex/OpenSpec for unit tests, or the active repo. Use `tests/fixtures/` (OpenSpec projects, lifecycle states, backends, git, config).
- TUI tests use Textual `run_test`/pilot with fake services — never require a real agent or OpenSpec install.
- Contract tests: every adapter implementation (WorkspaceReader, OpenSpecCLIAdapter, AgentBackend, ProcessRunner, GitInspector, etc.) runs the same contract suite.
- Optional real-CLI tests only behind `OPENSPEC_INTEGRATION_TESTS=1`; never required for a normal PR.
- Skip/xfail need written justification. No hiding flakes with retries.

## Quality gates (before archive)

`ruff check .` clean · `mypy src` clean · `pytest` green · Python 3.11 green · coverage targets met (domain 95%, security 90%, adapters 85%, total 80%) · docs updated · no critical security findings · `/opsx:verify` current.

## Key files

- `README.md` — product overview, architecture, stack, shortcuts, config, roadmap.
- `docs/01-construction-plan.md` — phases and change sequence.
- `docs/05-change-lifecycle-rules.md` — Kanban states and transitions.
- `docs/07-security-model.md` — security rules (binding).
- `docs/08-testing-strategy.md` — test levels, fixtures, CI matrix.
- `docs/10-definition-of-done.md` — DoD checklist (binding).
- `openspec/` — specs and changes; the source of truth for what to build.