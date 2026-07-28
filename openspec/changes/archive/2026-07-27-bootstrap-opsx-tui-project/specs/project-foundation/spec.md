## ADDED Requirements

### Requirement: Python package with entry point
The project SHALL provide an installable Python package `opsx_tui` under a `src/` layout with a `opsx-tui` console script entry point. The package SHALL declare `python_requires = ">=3.11"` and be installable via `python -m pip install -e ".[dev]"`.

#### Scenario: Fresh dev install
- **WHEN** a developer runs `python -m pip install -e ".[dev]"` in the repo root
- **THEN** the `opsx-tui` command is available on PATH and `python -c "import opsx_tui"` succeeds

#### Scenario: Entry point launches the app
- **WHEN** a user runs `opsx-tui` with no arguments
- **THEN** a Textual application window appears and the process exits cleanly when the user presses `q` or `Ctrl+C`

#### Scenario: Python 3.11 floor enforced
- **WHEN** the package is installed on Python 3.10
- **THEN** pip refuses installation with a version-incompatibility error

### Requirement: Hexagonal package skeleton
The package SHALL contain four layers: `presentation/`, `application/`, `domain/`, `infrastructure/`. Dependencies SHALL point inward only: `presentation` and `infrastructure` may depend on `application` and `domain`; `application` may depend on `domain`; `domain` SHALL NOT import from any other layer or from Textual.

#### Scenario: Domain has no outward imports
- **WHEN** `ruff check src/opsx_tui/domain/` is run
- **THEN** no import of `textual`, `logging`, `pathlib` filesystem operations, or any other layer package is flagged

#### Scenario: Presentation does not touch infrastructure
- **WHEN** `ruff check src/opsx_tui/presentation/` is run with import rules
- **THEN** no direct import of `opsx_tui.infrastructure` modules is present

### Requirement: Minimal Textual application shell
The `opsx-tui` entry point SHALL launch a Textual `App` that displays a placeholder welcome screen. The app SHALL exit on `q` and `Ctrl+C`. The app SHALL NOT access the filesystem or spawn subprocesses.

#### Scenario: App exits on q
- **WHEN** the app is running and the user presses `q`
- **THEN** the app closes and the process exits with code 0

#### Scenario: App exits on Ctrl+C
- **WHEN** the app is running and the user presses `Ctrl+C`
- **THEN** the app closes and the process exits with code 0

#### Scenario: TUI smoke test
- **WHEN** `pytest tests/tui/test_app_shell.py` is run with Textual's `run_test`
- **THEN** the app launches, the welcome screen is visible, and pressing `q` exits cleanly

### Requirement: Configuration models
The system SHALL define Pydantic 2 models for configuration: `Config` (top-level), `BackendConfig`, `ExecutionConfig`, and `UIConfig`. Models SHALL validate types and reject unknown keys. Models SHALL NOT store secrets.

#### Scenario: Valid config loads
- **WHEN** a TOML dict matching the schema is passed to `Config.model_validate`
- **THEN** a `Config` instance is returned with all fields populated

#### Scenario: Unknown key rejected
- **WHEN** a TOML dict with an unknown top-level key is passed to `Config.model_validate`
- **THEN** validation raises a `ValidationError`

#### Scenario: Secret field rejected
- **WHEN** a config dict contains a key named `api_key` or `token` at any level
- **THEN** validation raises a `ValidationError` with a message indicating secrets must not be stored in config

### Requirement: Hierarchical config loading
The system SHALL load configuration in precedence order: defaults < global (`~/.config/opsx-tui/config.toml`) < project (`.opsx-tui/config.toml`) < environment (`OPSX_TUI_*`) < CLI args. The loader SHALL return a validated `Config` instance. Missing config files SHALL NOT cause errors; they SHALL be treated as empty.

#### Scenario: Defaults only when no files exist
- **WHEN** no global, project, or env config is present
- **THEN** the loader returns a `Config` with all default values

#### Scenario: Project overrides global
- **WHEN** global config sets `theme = "dark"` and project config sets `theme = "opsx-dark"`
- **THEN** the resolved `Config.theme` equals `"opsx-dark"`

#### Scenario: Environment overrides project
- **WHEN** project config sets `execution.default_timeout_seconds = 1800` and `OPSX_TUI_EXECUTION__DEFAULT_TIMEOUT_SECONDS=60` is set
- **THEN** the resolved `Config.execution.default_timeout_seconds` equals `60`

#### Scenario: Missing config file is ignored
- **WHEN** the global config path does not exist
- **THEN** the loader skips it without error and continues with the next layer

#### Scenario: Malformed TOML raises a clear error
- **WHEN** a config file contains invalid TOML syntax
- **THEN** the loader raises a `ConfigLoadError` with the file path and underlying parse error

### Requirement: Config loader port
The system SHALL define a `ConfigLoader` Protocol in `domain/` with a `load() -> Config` method. A `TomlConfigLoader` adapter SHALL implement this port in `infrastructure/` using `tomllib` and `platformdirs`. The domain layer SHALL NOT import the adapter directly.

#### Scenario: Domain depends on port not adapter
- **WHEN** `ruff check src/opsx_tui/domain/` is run
- **THEN** no import of `opsx_tui.infrastructure.toml_config_loader` is present

#### Scenario: Adapter can be swapped in tests
- **WHEN** a test provides a fake `ConfigLoader` implementation to the application service
- **THEN** the application loads config from the fake without touching the filesystem

### Requirement: Structured logging with redaction hook
The system SHALL define a `Logger` Protocol in `domain/` with `info`, `warning`, `error`, and `debug` methods. A `StdlibLogger` adapter SHALL implement this port in `infrastructure/` wrapping `logging`. The adapter SHALL apply a `Redactor` to every record before emission. No secret patterns SHALL appear in log output.

#### Scenario: Redaction removes known secrets
- **WHEN** a log message contains a value matching a registered redaction pattern
- **THEN** the emitted log record contains `[REDACTED]` in place of the value

#### Scenario: Non-sensitive text preserved
- **WHEN** a log message contains no secret patterns
- **THEN** the emitted log record matches the original message exactly

### Requirement: Quality toolchain configured
The project SHALL configure Ruff, MyPy, and Pytest in `pyproject.toml`. Ruff SHALL fail on lint errors. MyPy SHALL run in strict mode on `src/opsx_tui/domain/` and `src/opsx_tui/application/`. Pytest SHALL use `asyncio_mode = "auto"`. Coverage SHALL target: domain 95%, security 90%, adapters 85%, total 80%.

#### Scenario: Ruff clean
- **WHEN** `ruff check .` is run
- **THEN** it exits 0 with no errors

#### Scenario: MyPy clean
- **WHEN** `mypy src` is run
- **THEN** it exits 0 with no errors

#### Scenario: Pytest green
- **WHEN** `pytest` is run
- **THEN** all tests pass and coverage thresholds are met

### Requirement: CI matrix across Python 3.11–3.14
The project SHALL define a GitHub Actions CI workflow with a Python matrix of `[3.11, 3.12, 3.13, 3.14]`. Python 3.11 SHALL be the mandatory gate: a failure on 3.11 blocks merge. Lint and type-check SHALL run on 3.11. Full tests SHALL run on 3.11 and 3.14. Reduced (unit-only) tests SHALL run on 3.12 and 3.13.

#### Scenario: 3.11 failure blocks
- **WHEN** the CI run on Python 3.11 fails
- **THEN** the overall CI status is failure

#### Scenario: 3.14 failure does not block if 3.11 passes
- **WHEN** the CI run on Python 3.14 fails but 3.11 passes
- **THEN** the 3.14 job is marked `continue-on-error` and the overall status is success

### Requirement: Test isolation invariants
The `tests/conftest.py` SHALL enforce that no test uses the real home directory, real credentials, or writes outside `tmp_path`. Environment variables prefixed `OPSX_TUI_` SHALL be cleared before each test. A `HOME` environment override SHALL point to a per-test tmp directory.

#### Scenario: Real home not used
- **WHEN** any test runs
- **THEN** `HOME` is set to a tmp path and `~/.config/opsx-tui/` does not resolve to the real user config dir

#### Scenario: OPSX_TUI env vars cleared
- **WHEN** a test does not explicitly set an `OPSX_TUI_*` variable
- **THEN** no `OPSX_TUI_*` variable is present in the test's environment

### Requirement: Architecture documentation
The project SHALL include `docs/architecture.md` documenting the four-layer hexagonal architecture, the dependency direction rule, and the list of forbidden imports per layer.

#### Scenario: Architecture doc exists and is referenced
- **WHEN** a developer opens `docs/architecture.md`
- **THEN** it describes the presentation, application, domain, and infrastructure layers and the allowed dependency direction