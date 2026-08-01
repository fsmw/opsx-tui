## Context

The Textual TUI framework runs its UI rendering and event loop on a single asyncio thread. Any synchronous CPU-bound or disk I/O operations block this thread, causing the UI to freeze or stutter. Currently, the `OpsxTuiApp.on_mount` lifecycle event and the `WorkspaceWatcherService._fire` file-watcher event perform synchronous OpenSpec workspace snapshots, reading numerous files. This blocks the UI thread at startup and during any file changes.

## Goals / Non-Goals

**Goals:**
- Eliminate UI freezing during startup by moving workspace parsing to a background thread.
- Eliminate UI stuttering when files are saved by moving watcher-triggered workspace parsing to a background thread.
- Ensure all Textual mutation happens on the main thread.

**Non-Goals:**
- Complete rewrite of the WorkspaceService.
- Adding new watcher capabilities (e.g. debouncing improvements) beyond fixing the blocking constraint.

## Decisions

1. **Use `asyncio.to_thread` for `WorkspaceService.read_snapshot`**: We will wrap the synchronous snapshot reads in `asyncio.to_thread`. This runs the blocking operation in the default asyncio thread pool, allowing the main event loop to continue rendering the TUI.
2. **Convert `on_mount` to `async def on_mount`**: Textual supports asynchronous `on_mount` methods. Making `on_mount` async allows us to `await asyncio.to_thread` directly inside it without needing a separate background task.
3. **Keep `_on_change` execution on the main thread**: Because `asyncio.to_thread` yields back to the main thread once the thread pool returns, the subsequent callback to `self._on_change(snapshot)` (which mutates the Textual state and triggers `BoardView.reload()`) will naturally run on the main thread, satisfying Textual's thread-safety constraints.

## Risks / Trade-offs

- **Risk: Threads may raise exceptions in different ways.** Mitigation: Ensure that standard exception blocks (`except Exception:`) in `app.py` and `workspace_watcher_service.py` properly catch and handle errors returned by the thread pool.
- **Trade-off: Minimal overhead.** Creating thread pool tasks has marginal overhead, but this is negligible compared to the cost of blocking the UI.
