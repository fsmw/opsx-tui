# Detect OpenSpec CLI

## What

Detect the `openspec` CLI executable in the user's PATH, query its version and
available commands, and produce a structured healthcheck with diagnostics — all
without executing any modifying operation.

## Why

OPSX TUI needs to know whether `openspec` is available, which version is
installed, and what commands it supports before it can execute CLI operations
(Fase 4). This detection is the foundation for every subsequent CLI interaction:
command palette, runner, agent orchestration.

Without detection, the app would either crash trying to invoke a missing
executable or silently fail, leaving the user confused.

## Scope

### In scope

-   Detect `openspec` executable via `shutil.which`
-   Query version via `openspec --version`
-   Parse semver tuple from version string
-   Compare against minimum compatible version
-   List available commands via `openspec list --json` (fallback `--help`)
-   Produce `OpenSpecCLIInfo` model with path, version, compatibility, commands, diagnostics
-   `OpenSpecCLIDetector` port (async Protocol) in domain
-   `ProcessOpenSpecCLIDetector` adapter in infrastructure
-   Application service to wrap detector + compatibility check
-   Wire into Container
-   Integrate with app startup (detect on load, store in app state)
-   Show CLI status in a new section of the shell header or Settings view
-   Full test coverage: unit, contract, integration, fixture-based

### Out of scope

-   Executing `openspec` commands that modify state (next change)
-   Command palette or runner UI
-   Agent backend detection
-   Persistence of detection results
-   Auto-installation or download of OpenSpec CLI

## Impact

-   New domain models: `OpenSpecCLIInfo` (frozen), `CLIVersionMinimum` constant
-   New port: `OpenSpecCLIDetector` (async Protocol)
-   New adapter: `ProcessOpenSpecCLIDetector`
-   New service: `OpenSpecCLIDetectionService`
-   Container extended with detection wiring
-   `OpsxTuiApp` extended with CLI state and detection on load
-   New fixture directories for CLI detection tests
-   ~250 lines of production code, ~350 lines of test code
-   No new runtime dependencies (uses stdlib `shutil` + `asyncio.create_subprocess_exec`)
