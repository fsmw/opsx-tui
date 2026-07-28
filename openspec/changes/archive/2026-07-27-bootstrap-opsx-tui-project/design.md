## Context

OPSX TUI is greenfield. No `pyproject.toml`, `src/`, or `tests/` exist. The README and `docs/01–10` define the product spec, architecture, lifecycle, security, testing, and DoD. This change creates the runnable foundation: a Python package, a minimal Textual app, config loading, logging, the hexagonal skeleton, and the quality toolchain. All subsequent changes build on this base.

Constraints from the docs:
- Python 3.11 is the mandatory minimum (CI gate, never skip).
- Hexagonal layering: `presentation → application → domain ← infrastructure`. Dependencies point inward only.
- No `shell=True`, no secrets in TOML/SQLite, no filesystem access from presentation, no Textual import in domain.
- Config precedence: defaults < global < project < env < CLI < session.
- Tests must not use the real home dir, real credentials, or the active repo.

## Goals / Non-Goals

**Goals:**
- A installable Python package (`pip install -e ".[dev]"`) with the `opsx-tui` entry point.
- A minimal Textual app that launches and exits cleanly via keyboard.
- Pydantic 2 config models and a hierarchical TOML loader with the documented precedence chain.
- Structured logging via a port + stdlib adapter, redaction-ready.
- The four-layer package skeleton with empty `__init__.py` files marking layer boundaries.
- Ruff, MyPy (strict on `src`), Pytest + pytest-asyncio + Hypothesis wired up.
- CI matrix across Python 3.11–3.14 with 3.11 as the mandatory gate.
- A `tests/` tree with the documented subdirectories and a `conftest.py` enforcing isolation invariants.
- `docs/architecture.md` documenting the layering contract.

**Non-Goals:**
- OpenSpec project discovery or workspace reading (Change `discover-openspec-project`).
- Kanban, lifecycle inference, task parsing (later changes).
- Subprocess execution, agent backends, Git integration (later phases).
- SQLite persistence functional (schema deferred; only the path is reserved).
- watchfiles watcher active (dependency declared, not wired).
- Theming, plugins, distribution packaging.

## Decisions

### D1: `src/` layout over flat layout
**Choice:** `src/opsx_tui/` package.
**Why:** Prevents accidental imports from cwd, enforces that tests run against the installed package, matches the structure documented in `docs/01-construction-plan.md` §4.4.
**Alternatives:** Flat layout (`opsx_tui/` at root) — rejected because it allows importing unbuilt code and the docs already specify `src/`.

### D2: `tomllib` (stdlib) for parsing, `platformdirs` for paths
**Choice:** Use `tomllib` (stdlib in Python 3.11+) for TOML parsing. Use `platformdirs` for `~/.config/opsx-tui/` resolution.
**Why:** `tomllib` is in the stdlib since 3.11 (our minimum), so no extra dependency. `platformdirs` handles cross-platform config dirs correctly.
**Alternatives:** `tomli` (backport) — unnecessary given 3.11 floor. `rtoml`/`tomli-w` for writing — not needed yet (config is read-only at this stage).

### D3: Config models in domain, loader in infrastructure
**Choice:** `Config`, `BackendConfig`, `ExecutionConfig` as Pydantic 2 models in `domain/`. `ConfigLoader` port (Protocol) in `domain/`. `TomlConfigLoader` adapter in `infrastructure/`.
**Why:** Keeps domain pure (no filesystem I/O), infrastructure swappable, and matches the hexagonal rule. Enables unit-testing config merging without touching the filesystem.
**Alternatives:** Put loading in application — rejected because application orchestrates, infrastructure performs I/O.

### D4: Hierarchical merge via immutable reduction
**Choice:** Config resolution is a pure function: `merge(defaults, global, project, env, cli) -> Config`. Each layer produces a partial dict; the merge applies in precedence order. Environment variables use `OPSX_TUI_` prefix with `__` as section separator (e.g., `OPSX_TUI_EXECUTION__DEFAULT_TIMEOUT_SECONDS`).
**Why:** Deterministic, testable without files, and the precedence chain is explicit in code.
**Alternatives:** Layered Pydantic model overrides — rejected as harder to test and reason about than a dict merge + final validation.

### D5: Logging via port, stdlib adapter, redaction hook
**Choice:** `Logger` Protocol in `domain/`. `StdlibLogger` adapter in `infrastructure/` wrapping `logging`. A `Redactor` takes a set of patterns; the adapter applies it to every record.
**Why:** Keeps domain free of `logging` import, makes redaction testable, and defers structured logging (e.g., `structlog`) to a later change without breaking the port.
**Alternatives:** `structlog` now — rejected as premature; port allows swapping later.

### D6: Minimal Textual app — single screen, exit on `q`/`Ctrl+C`
**Choice:** `OpsxTuiApp(App)` in `presentation/` with a placeholder "Welcome" screen. Binds `q` and `Ctrl+C` to `app.exit()`.
**Why:** Proves the framework wiring works and gives a runnable smoke test. No views, no data — just the shell.
**Alternatives:** No app yet — rejected because the entry point must launch something real for the CI smoke test.

### D7: Quality config in `pyproject.toml`
**Choice:** Ruff (line-length 88, select E/F/I/UP/B), MyPy (`strict` on `src/opsx_tui/domain/` and `application/`, `strict_optional` everywhere), Pytest with `asyncio_mode = "auto"`, coverage thresholds in `[tool.coverage]`.
**Why:** Single source of truth for tooling, no scattered config files.
**Alternatives:** Separate `ruff.toml`/`mypy.ini` — rejected as fragmentation.

### D8: CI matrix — full suite on 3.11 and 3.14, reduced on 3.12/3.13
**Choice:** GitHub Actions matrix: `[3.11, 3.12, 3.13, 3.14]`. Lint + type-check on 3.11 only. Full tests on 3.11 and 3.14. Smoke (unit only) on 3.12 and 3.13. Package build on 3.11.
**Why:** Matches `docs/08-testing-strategy.md` §26.3. 3.11 is the mandatory gate; 3.14 is the dev version. Reduced runs on intermediate versions save CI minutes while catching syntax/stdlib drift.
**Alternatives:** Full suite on all four — rejected as wasteful per the testing strategy doc.

### D9: `conftest.py` isolation invariants
**Choice:** Root `tests/conftest.py` sets `HOME` to a tmp dir, clears `OPSX_TUI_*` env vars, and asserts no test writes outside `tmp_path`.
**Why:** Enforces the testing invariants from `docs/08` §36 (no real home, no real credentials, no writes outside temp) at the framework level rather than relying on discipline.
**Alternatives:** Per-test fixtures — rejected as easy to forget.

## Risks / Trade-offs

- **[Risk] Textual API churn across versions** → Pin a compatible Textual version range in `pyproject.toml`; TUI tests use `run_test`/pilot which are stable.
- **[Risk] Python 3.14 still in beta at implementation time** → Use `3.14` in matrix but allow the job to be `continue-on-error: true` until stable; 3.11 remains the real gate.
- **[Risk] `tomllib` read-only (no writing)** → Acceptable; config writing is deferred. If needed later, add `tomli-w` as an optional dep.
- **[Trade-off] Empty layer packages** → The `domain/`, `application/`, `infrastructure/`, `presentation/` `__init__.py` files are empty now. This is intentional: they establish the import boundary and will be populated by later changes.
- **[Trade-off] watchfiles declared but unused** → Declared in deps so the lockfile is stable, but not imported. Accepted to avoid a dependency churn in a later change.