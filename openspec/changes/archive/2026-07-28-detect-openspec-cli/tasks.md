# Tasks: Detect OpenSpec CLI

## 1. Domain model — OpenSpecCLIInfo

- [x] 1.1 Create `domain/openspec_cli.py` with `OpenSpecCLIInfo` frozen Pydantic model (path, version, version_tuple, is_compatible, available_commands, diagnostics)
- [x] 1.2 Add `CLI_VERSION_MINIMUM = (0, 1, 0)` constant
- [x] 1.3 Export from `domain/__init__.py`

## 2. Domain port — OpenSpecCLIDetector

- [x] 2.1 Add `OpenSpecCLIDetector` async Protocol to `domain/ports.py`

## 3. Infrastructure adapter — ProcessOpenSpecCLIDetector

- [x] 3.1 Create `infrastructure/cli_detector.py` with `ProcessOpenSpecCLIDetector` class
- [x] 3.2 Implement executable detection via `shutil.which(\"openspec\")`
- [x] 3.3 Implement version query via `asyncio.create_subprocess_exec(\"openspec\", \"--version\")` with 10s timeout
- [x] 3.4 Implement version parsing via regex `r\"(\\d+)\\.(\\d+)\\.(\\d+)\"`
- [x] 3.5 Implement compatibility comparison against `CLI_VERSION_MINIMUM`
- [x] 3.6 Implement available commands via `openspec list --json` with `--help` fallback
- [x] 3.7 Handle all error modes: FileNotFoundError, TimeoutError, CalledProcessError, OSError → diagnostics

## 4. Application service — OpenSpecCLIDetectionService

- [x] 4.1 Create `application/cli_detection_service.py` with `OpenSpecCLIDetectionService` (wraps detector, runs detect, returns info)
- [x] 4.2 Export from `application/__init__.py`

## 5. Container wiring

- [x] 5.1 Add `create_cli_detector()` factory method to `Container` (returns ProcessOpenSpecCLIDetector)
- [x] 5.2 Add `run_cli_detection()` method to `Container` (runs detection, returns info)
- [x] 5.3 Ensure existing tests still pass after wiring

## 6. App integration

- [x] 6.1 Add `cli_info: OpenSpecCLIInfo | None` state to `OpsxTuiApp`
- [x] 6.2 Run detection via `asyncio.create_task` after workspace load
- [x] 6.3 Add CLI status section to Settings view (path, version, compatibility indicator)
- [x] 6.4 Re-run detection on workspace change callback

## 7. Fixtures

- [x] 7.1 Create `tests/fixtures/cli_detection/__init__.py`
- [x] 7.2 Add `FakeOpenSpecCLIDetector` fixture (configurable: path, version, commands, fail mode)
- [x] 7.3 Create fixture for version strings (standard, unparseable, dev)
- [x] 7.4 Create fixture for `openspec list --json` output samples

## 8. Tests

### Unit — domain models
- [x] 8.1 Test `OpenSpecCLIInfo` frozen invariant and default state

### Unit — ProcessOpenSpecCLIDetector
- [x] 8.2 Test detection with available executable (mock shutil.which + subprocess)
- [x] 8.3 Test detection with missing executable
- [x] 8.4 Test version parsing (standard, unparseable, empty output)
- [x] 8.5 Test compatibility check (meets minimum, below minimum, unknown)
- [x] 8.6 Test available commands (JSON success, help fallback, both fail)
- [x] 8.7 Test all error modes (timeout, non-zero, permission denied)

### Contract — CLIDetector
- [x] 8.8 Test that ProcessOpenSpecCLIDetector conforms to OpenSpecCLIDetector Protocol

### Integration — real subprocess (optional, OPENSPEC_INTEGRATION_TESTS=1)
- [ ] 8.9 Test detection against real `openspec` binary (optional, gated — deferred)

### TUI — Settings view
- [x] 8.10 Test that Settings view shows CLI status
- [x] 8.11 Test that Settings shows "not found" when CLI absent

## 9. Quality verification

- [x] 9.1 Run `ruff check .` — zero issues
- [x] 9.2 Run `mypy src` — zero issues
- [x] 9.3 Run `pytest` — all tests pass (including existing)
- [ ] 9.4 Run `pytest` on Python 3.11 (CI gate — requires Python 3.11 environment)
