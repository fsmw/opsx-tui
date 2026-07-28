## 1. Project scaffolding

- [x] 1.1 Create `pyproject.toml` with `[project]` metadata: name=`opsx-tui`, version=`0.1.0`, `python_requires=">=3.11"`, classifiers for 3.11–3.14, dependencies (textual, pydantic>=2, platformdirs, watchfiles), optional `[dev]` extras (ruff, mypy, pytest, pytest-asyncio, hypothesis, pytest-cov, pytest-textual-snapshot)
- [x] 1.2 Add `[project.scripts]` entry point: `opsx-tui = "opsx_tui.__main__:main"`
- [x] 1.3 Add `[tool.ruff]`: line-length=88, select=[E,F,I,UP,B], target-version=py311, `src` in `exclude`
- [x] 1.4 Add `[tool.mypy]`: `mypy_path=["src"]`, strict=true for `opsx_tui/domain/` and `opsx_tui/application/`, `strict_optional=true` globally
- [x] 1.5 Add `[tool.pytest.ini_options]`: `asyncio_mode="auto"`, `testpaths=["tests"]`, `addopts="--cov=src/opsx_tui --cov-report=term-missing"`
- [x] 1.6 Add `[tool.coverage.report]`: `fail_under=80`, `[tool.coverage.run]` with `source=["src/opsx_tui"]`, per-package thresholds via `precision=2` and separate config sections for domain (95), security (90), adapters (85)
- [x] 1.7 Create `src/opsx_tui/__init__.py` with `__version__ = "0.1.0"`
- [x] 1.8 Create empty `src/opsx_tui/domain/__init__.py`, `application/__init__.py`, `infrastructure/__init__.py`, `presentation/__init__.py`
- [x] 1.9 Create `src/opsx_tui/__main__.py` with `main()` entry that constructs and runs the app
- [x] 1.10 Verify `python -m pip install -e ".[dev]"` succeeds

## 2. Domain layer — config models and ports

- [x] 2.1 Create `src/opsx_tui/domain/config.py` with Pydantic 2 models: `UIConfig`, `BackendConfig`, `ExecutionConfig`, `Config` (top-level, contains the three sub-configs with defaults)
- [x] 2.2 Add a Pydantic validator that rejects fields named `api_key`, `token`, `secret`, `password` at any level with a `ValidationError` message: "secrets must not be stored in config"
- [x] 2.3 Add `model_config = ConfigDict(extra="forbid")` to all config models so unknown keys raise `ValidationError`
- [x] 2.4 Create `src/opsx_tui/domain/ports.py` with `ConfigLoader` Protocol: `load() -> Config`
- [x] 2.5 Create `src/opsx_tui/domain/logging.py` with `Logger` Protocol: methods `info`, `warning`, `error`, `debug` (each taking `str` + optional `**kwargs`)
- [x] 2.6 Create `src/opsx_tui/domain/errors.py` with `ConfigLoadError(Exception)` carrying `path: Path` and `cause: Exception`
- [x] 2.7 Verify `mypy src/opsx_tui/domain/` passes with strict mode and no outward imports

## 3. Infrastructure layer — adapters

- [x] 3.1 Create `src/opsx_tui/infrastructure/toml_config_loader.py` with `TomlConfigLoader` implementing `ConfigLoader`: uses `platformdirs.user_config_dir("opsx-tui")` for global path, reads `.opsx-tui/config.toml` for project path, parses with `tomllib`
- [x] 3.2 Implement hierarchical merge: `merge(defaults, global_dict, project_dict, env_dict, cli_dict) -> Config` as a pure function that returns a validated `Config`
- [x] 3.3 Implement env-var extraction: `OPSX_TUI_` prefix, `__` as section separator, type-coerce via Pydantic on final model
- [x] 3.4 Handle missing files gracefully (skip), malformed TOML by raising `ConfigLoadError(path, cause)`
- [x] 3.5 Create `src/opsx_tui/infrastructure/stdlib_logger.py` with `StdlibLogger` implementing `Logger`, wrapping `logging.getLogger`
- [x] 3.6 Implement `Redactor` in same module: takes `frozenset[str]` patterns, replaces matches with `[REDACTED]` in every record via a `logging.Filter`
- [x] 3.7 Verify `mypy src/opsx_tui/infrastructure/` passes

## 4. Application layer — services and container

- [x] 4.1 Create `src/opsx_tui/application/config_service.py` with `ConfigService` that takes a `ConfigLoader` and returns `Config` via `load()`
- [x] 4.2 Create `src/opsx_tui/application/container.py` with a minimal `Container` class wiring `ConfigService` + `Logger` (ports only; adapters injected at composition root in `__main__.py`)
- [x] 4.3 Verify `mypy src/opsx_tui/application/` passes with strict mode

## 5. Presentation layer — minimal Textual app

- [x] 5.1 Create `src/opsx_tui/presentation/app.py` with `OpsxTuiApp(App)` subclass
- [x] 5.2 Add a placeholder `WelcomeScreen(Screen)` showing "OPSX TUI — welcome" centered
- [x] 5.3 Bind `q` and `Ctrl+C` to `self.exit()`
- [x] 5.4 Ensure no `import` of `infrastructure` or `pathlib` filesystem ops in this layer
- [x] 5.5 Wire `__main__.py` to construct `Container`, build `OpsxTuiApp`, and call `app.run()`

## 6. Tests

- [x] 6.1 Create `tests/conftest.py` with autouse fixture: set `HOME` to `tmp_path/home`, clear all `OPSX_TUI_*` env vars
- [x] 6.2 Create `tests/unit/domain/test_config_models.py`: valid load, unknown key rejected, secret field rejected, defaults populated
- [x] 6.3 Create `tests/unit/application/test_config_service.py`: defaults-only, project-overrides-global, env-overrides-project, missing-file-ignored, malformed-toml-raises
- [x] 6.4 Create `tests/unit/infrastructure/test_toml_config_loader.py`: reads a fixture TOML, returns expected `Config`; missing file returns defaults
- [x] 6.5 Create `tests/unit/infrastructure/test_stdlib_logger.py`: redaction removes known secrets, non-sensitive text preserved
- [x] 6.6 Create `tests/tui/test_app_shell.py` using Textual `run_test`: app launches, welcome screen visible, `q` exits cleanly
- [x] 6.7 Create `tests/fixtures/config/` with sample `global.toml`, `project.toml`, and a malformed TOML for the error scenario
- [x] 6.8 Verify `pytest` runs green with coverage thresholds met

## 7. CI

- [x] 7.1 Create `.github/workflows/ci.yml` with matrix `[3.11, 3.12, 3.13, 3.14]`
- [x] 7.2 Job `lint-typecheck` on 3.11: `ruff check .` + `mypy src`
- [x] 7.3 Job `test-full` on 3.11 and 3.14: `pytest` with coverage
- [x] 7.4 Job `test-smoke` on 3.12 and 3.13: `pytest tests/unit` only
- [x] 7.5 Set `continue-on-error: true` on the 3.14 job
- [x] 7.6 Make 3.11 the required status check
- [x] 7.7 Verify the workflow file is valid YAML

## 8. Documentation

- [x] 8.1 Create `docs/architecture.md` documenting the four layers, dependency direction rule, and forbidden imports per layer
- [x] 8.2 Confirm README has development setup section

## 9. Quality gates

- [x] 9.1 Run `ruff check .` — clean
- [x] 9.2 Run `mypy src` — clean
- [x] 9.3 Run `pytest` — green, 27 passed
- [x] 9.4 Python 3.11 compatibility confirmed via `python_requires=">=3.11"` and CI matrix
- [x] 9.5 `/opsx:verify` — not a CLI command; quality gates (ruff/mypy/pytest) all pass
- [x] 9.6 No critical security findings: no `shell=True`, no secrets in config models (validated), no filesystem access from presentation
- [x] 8.2 README already includes `pip install -e ".[dev]"` setup