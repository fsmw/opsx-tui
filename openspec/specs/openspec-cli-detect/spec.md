# OpenSpec CLI Detection

## Purpose

Detect the `openspec` CLI executable, query its version and capabilities, and
produce a structured healthcheck with diagnostics — the foundation for all
subsequent CLI command execution.

---

## Requirements

### REQ-CLI-DETECT-01 — Frozen detection model

**OpenSpecCLIInfo** SHALL be a frozen Pydantic model with fields: `path`,
`version`, `version_tuple`, `is_compatible`, `available_commands`,
`diagnostics`.

#### Scenario: Model is frozen
- **GIVEN** an OpenSpecCLIInfo instance
- **WHEN** attempting to mutate any field
- **THEN** a `FrozenInstanceError` SHALL be raised

#### Scenario: Default state for missing CLI
- **GIVEN** OpenSpecCLIInfo constructed with no arguments
- **THEN** `path` SHALL be `None`
- **AND** `version` SHALL be `None`
- **AND** `version_tuple` SHALL be `None`
- **AND** `is_compatible` SHALL be `False`
- **AND** `available_commands` SHALL be empty
- **AND** `diagnostics` SHALL be empty

---

### REQ-CLI-DETECT-02 — Executable detection via PATH

The detector SHALL use `shutil.which("openspec")` to locate the executable.

#### Scenario: Found in PATH
- **GIVEN** an `openspec` executable exists in a directory on PATH
- **WHEN** `detect()` is called
- **THEN** `path` SHALL be the resolved absolute path

#### Scenario: Not found in PATH
- **GIVEN** no `openspec` executable exists on PATH
- **WHEN** `detect()` is called
- **THEN** `path` SHALL be `None`
- **AND** `is_compatible` SHALL be `False`
- **AND** diagnostics SHALL contain an ERROR level diagnostic

---

### REQ-CLI-DETECT-03 — Version query

The detector SHALL execute `openspec --version` to obtain the installed version.

#### Scenario: Version query succeeds
- **GIVEN** `openspec --version` outputs "openspec 0.2.1"
- **WHEN** the output is parsed
- **THEN** `version` SHALL be `"0.2.1"`
- **AND** `version_tuple` SHALL be `(0, 2, 1)`

#### Scenario: Version query times out
- **GIVEN** `openspec --version` does not respond within 10 seconds
- **WHEN** detection completes
- **THEN** `version` SHALL be `None`
- **AND** a WARNING diagnostic SHALL be added

#### Scenario: Version query non-zero exit
- **GIVEN** `openspec --version` exits with code 1
- **WHEN** detection completes
- **THEN** `version` SHALL be `None`
- **AND** a WARNING diagnostic SHALL be added

#### Scenario: Unparseable version string
- **GIVEN** `openspec --version` outputs "openspec development"
- **WHEN** the output is parsed
- **THEN** `version` SHALL be `"openspec development"`
- **AND** `version_tuple` SHALL be `None`
- **AND** a WARNING diagnostic SHALL be added

---

### REQ-CLI-DETECT-04 — No shell=True

The detector SHALL NOT use `shell=True` for any subprocess invocation. All
arguments SHALL be passed as a list.

#### Scenario: Args are a list
- **GIVEN** any subprocess invocation
- **WHEN** inspecting the call
- **THEN** args SHALL be a `list[str]`
- **AND** `shell` SHALL be `False`

---

### REQ-CLI-DETECT-05 — Compatibility check

The detector SHALL compare the parsed version against a minimum version constant.

#### Scenario: Version meets minimum
- **GIVEN** `CLI_VERSION_MINIMUM = (0, 1, 0)`
- **AND** detected `version_tuple = (0, 2, 1)`
- **WHEN** compatibility is evaluated
- **THEN** `is_compatible` SHALL be `True`

#### Scenario: Version below minimum
- **GIVEN** `CLI_VERSION_MINIMUM = (0, 1, 0)`
- **AND** detected `version_tuple = (0, 0, 9)`
- **WHEN** compatibility is evaluated
- **THEN** `is_compatible` SHALL be `False`
- **AND** a WARNING diagnostic SHALL be added

#### Scenario: Unknown version
- **GIVEN** `version_tuple` is `None`
- **WHEN** compatibility is evaluated
- **THEN** `is_compatible` SHALL be `False`

---

### REQ-CLI-DETECT-06 — Available commands

The detector SHALL attempt to list available commands.

#### Scenario: JSON list succeeds
- **GIVEN** `openspec list --json` returns `["new","status","validate"]`
- **WHEN** detection completes
- **THEN** `available_commands` SHALL contain those command names

#### Scenario: JSON list fails, help fallback
- **GIVEN** `openspec list --json` fails
- **AND** `openspec --help` returns parseable output
- **WHEN** detection completes
- **THEN** `available_commands` MAY contain extracted command names

#### Scenario: Both methods fail
- **GIVEN** both `openspec list --json` and `openspec --help` fail
- **WHEN** detection completes
- **THEN** `available_commands` SHALL be empty
- **AND** a WARNING diagnostic SHALL be added

---

### REQ-CLI-DETECT-07 — Port is async Protocol

`OpenSpecCLIDetector` SHALL be a `typing.Protocol` with an async `detect`
method.

#### Scenario: Protocol conformance
- **GIVEN** `ProcessOpenSpecCLIDetector` implements `OpenSpecCLIDetector`
- **WHEN** checked at runtime
- **THEN** `isinstance(detector, OpenSpecCLIDetector)` SHALL raise `TypeError`
  (Protocol checking with `@runtime_checkable`)

#### Scenario: Async signature
- **GIVEN** the `detect` method
- **WHEN** inspecting its return type
- **THEN** it SHALL be `Coroutine[Any, Any, OpenSpecCLIInfo]`

---

### REQ-CLI-DETECT-08 — Error resilience

Every subprocess call SHALL be wrapped in try/except for `OSError`,
`asyncio.TimeoutError`, and produce a diagnostic instead of crashing.

#### Scenario: Permission denied
- **GIVEN** the `openspec` executable exists but is not executable
- **WHEN** the detector attempts to run it
- **THEN** an ERROR diagnostic SHALL be added
- **AND** detection SHALL complete without raising

#### Scenario: Timeout
- **GIVEN** the subprocess hangs
- **WHEN** `asyncio.wait_for` raises `TimeoutError`
- **THEN** a WARNING diagnostic SHALL be added
- **AND** detection SHALL complete without raising

---

### REQ-CLI-DETECT-09 — Detection on startup

The TUI app SHALL run CLI detection when loading a workspace and store the
result.

#### Scenario: Detection runs on workspace load
- **GIVEN** the app is loading a workspace
- **WHEN** workspace loading completes
- **THEN** `OpenSpecCLIDetector.detect()` SHALL have been called

#### Scenario: CLI info accessible from app
- **GIVEN** detection has completed
- **WHEN** accessing app state
- **THEN** the `OpenSpecCLIInfo` result SHALL be available

---

### REQ-CLI-DETECT-10 — Container wiring

The Container SHALL provide factory methods for the detector and detection
service.

#### Scenario: Default detector
- **GIVEN** a Container instance
- **WHEN** `create_cli_detector()` is called
- **THEN** a `ProcessOpenSpecCLIDetector` SHALL be returned

#### Scenario: Detection via container
- **GIVEN** a Container instance with a detector
- **WHEN** `run_cli_detection()` is called
- **THEN** detection SHALL run and return `OpenSpecCLIInfo`

---

### REQ-CLI-DETECT-11 — CLI status in Settings view

The Settings view SHALL show a section with CLI detection status.

#### Scenario: CLI available
- **GIVEN** `openspec` was detected at version 0.2.1
- **WHEN** the user opens the Settings view
- **THEN** the view SHALL display the path and version

#### Scenario: CLI not available
- **GIVEN** `openspec` was not found
- **WHEN** the user opens the Settings view
- **THEN** the view SHALL display a "not found" indicator
