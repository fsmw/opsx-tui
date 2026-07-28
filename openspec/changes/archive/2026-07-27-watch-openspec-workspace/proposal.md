## Why

OPSX TUI currently reads the workspace once at startup. If the user edits a spec, completes a task, or archives a change from outside the app (or from a running agent), the TUI shows stale data until manually refreshed. For a tool that visualizes and operates OpenSpec projects, this is unacceptable: tasks get checked off, artifacts appear and disappear, and the Kanban must reflect reality.

A filesystem watcher solves this. By monitoring `openspec/` for changes via `watchfiles`, debouncing rapid events, and re-reading only when the fingerprint differs, the app stays current without polling or manual reloads.

## What Changes

- Add `WorkspaceObserver` Protocol in `domain/ports.py` for watching an `openspec/` directory.
- Implement `WatchfilesObserver` in `infrastructure/` wrapping `watchfiles.awatch()` as an async generator yielding batches of changed paths.
- Create `WorkspaceWatcherService` in `application/workspace_watcher_service.py` with debounce (500ms), fingerprint comparison, and a callback-based notification model.
- Add `start_watching(openspec_root, on_change)` and `stop()` lifecycle.
- Wire the watcher in `Container` and start it in `OpsxTuiApp.on_mount()` after the initial workspace load.
- Handle clean cancellation: `stop()` cancels the asyncio task and closes all resources.
- Handle errors: watcher logs and continues on transient filesystem errors; stops on critical errors.
- Add tests: debounce timing, fingerprint skip, event batching, clean cancellation, error resilience.

## Capabilities

### New Capabilities
- `workspace-monitoring`: Reactive filesystem watching for `openspec/` changes via watchfiles, debounce, fingerprint comparison, and callback-based notification.

### Modified Capabilities
- `project-foundation`: `watchfiles` dependency now used (was declared but unused).
- `tui-shell`: `OpsxTuiApp` starts the watcher after `_load_workspace` and refreshes `OpenSpecProject` on change.

## Impact

- New files: `application/workspace_watcher_service.py`, `infrastructure/watchfiles_observer.py`, `tests/unit/application/test_workspace_watcher_service.py`, `tests/integration/test_workspace_watcher.py`.
- Modified files: `domain/ports.py` (add `WorkspaceObserver`), `application/container.py` (wire watcher), `presentation/app.py` (start watcher, handle updates).
- Deps: `watchfiles` becomes a runtime dependency (previously declared but unused).
- No existing code broken: the watcher is opt-in started after initial load.