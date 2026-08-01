## Why

The current implementation performs synchronous file I/O operations inside the main asyncio event loop thread during startup (`OpsxTuiApp.on_mount`) and on file save (`WorkspaceWatcherService._fire`). Textual relies on this main thread to handle rendering and key events; blocking it causes the TUI to freeze and stutter noticeably. Moving these blocking operations to a background thread will ensure the UI remains responsive and conforms to standard asyncio and Textual UI constraints.

## What Changes

- Wrap synchronous file reading operations in background threads using `asyncio.to_thread`.
- Update `OpsxTuiApp.on_mount` to be an asynchronous method to await background thread execution.
- Maintain existing non-blocking operations like `run_cli_detection`.

## Capabilities

### New Capabilities
- `performance`: Defines non-functional constraints regarding UI responsiveness and threading.

### Modified Capabilities
None. This is an implementation-level bug fix to meet non-functional performance constraints; no functional requirements change.

## Impact

- `src/opsx_tui/presentation/app.py`: `on_mount` lifecycle event converted to async and blocking I/O deferred to thread.
- `src/opsx_tui/application/workspace_watcher_service.py`: `_fire` watcher event handler deferred to thread.
- UI responsiveness will significantly improve, completely eliminating freezes during file saves and startup.
