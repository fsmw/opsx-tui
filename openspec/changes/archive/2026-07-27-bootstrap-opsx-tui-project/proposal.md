## Why

OPSX TUI has no code yet. Before any capability can be built, the project needs a runnable Python package: an entry point, a minimal Textual app that opens and closes, hierarchical TOML config loading, logging, the four-layer hexagonal package skeleton, and the quality toolchain (Ruff, MyPy, Pytest) wired into CI across Python 3.11–3.14. This change establishes that foundation so every subsequent change can build on a stable, testable base.

## What Changes

- Add `pyproject.toml` with `opsx_tui` package, `opsx-tui` entry point, dev extras (Ruff, MyPy, Pytest, pytest-asyncio, Hypothesis, coverage), and Python `>=3.11` classifier.
- Create the `src/opsx_tui/` package with the four-layer skeleton: `domain/`, `application/`, `infrastructure/`, `presentation/`.
- Add `__main__.py` and `app.py` exposing a minimal Textual `App` that launches and exits on `q` / `Ctrl+C`.
- Add domain models for configuration (`Config`, `BackendConfig`, `ExecutionConfig`) using Pydantic 2, with TOML loading via a port (`ConfigLoader`) and a filesystem adapter.
- Implement hierarchical config resolution: defaults < global (`~/.config/opsx-tui/config.toml`) < project (`.opsx-tui/config.toml`) < environment (`OPSX_TUI_*`) < CLI args, using `platformdirs` for user paths.
- Add structured logging (redaction-ready) with a port (`Logger`) and a stdlib adapter.
- Add a minimal dependency container wiring the application services.
- Add `tests/` with `unit/`, `contract/`, `integration/`, `tui/`, `e2e/`, `fixtures/` directories and a `conftest.py` enforcing no-real-home / no-real-credentials invariants.
- Add Ruff, MyPy, and Pytest configuration in `pyproject.toml` (line length, strict mypy on `src`, coverage targets: domain 95%, security 90%, adapters 85%, total 80%).
- Add CI workflow (`.github/workflows/ci.yml`) with lint, type-check, unit/contract/integration/tui tests, and the Python 3.11–3.14 matrix (3.11 mandatory gate).
- Add `docs/architecture.md` documenting the hexagonal layering and dependency rules.

## Capabilities

### New Capabilities
- `project-foundation`: Package skeleton, entry point, minimal Textual app, config models and hierarchical loader, logging, dependency container, quality toolchain, and CI matrix.

### Modified Capabilities
<!-- None — this is the first change. -->

## Impact

- New files: `pyproject.toml`, `src/opsx_tui/**`, `tests/**`, `.github/workflows/ci.yml`, `docs/architecture.md`.
- New dependencies: textual, pydantic 2, platformdirs, tomllib (stdlib in 3.11+), watchfiles (deferred to later change but declared), ruff, mypy, pytest, pytest-asyncio, hypothesis, pytest-cov.
- No existing code affected (greenfield).
- Establishes the layering contract all future changes must respect: presentation → application → domain ← infrastructure.