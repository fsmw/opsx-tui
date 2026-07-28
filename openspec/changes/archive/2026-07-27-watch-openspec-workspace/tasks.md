## 1. Domain port

- [x] 1.1 Add `WorkspaceObserver` Protocol to `domain/ports.py` with `async def watch(self, path: Path) -> AsyncIterator[tuple[Path, ...]]`

## 2. Infrastructure observer

- [x] 2.1 Create `infrastructure/watchfiles_observer.py` with `WatchfilesObserver` implementing `WorkspaceObserver`
- [x] 2.2 Implement `watch()` using `watchfiles.awatch()` on `path / "openspec"`, yielding batches of changed paths
- [x] 2.3 Handle transient OSError: log warning and continue
- [x] 2.4 Handle cancellation: clean up resources on task cancellation

## 3. Application watcher service

- [x] 3.1 Create `application/workspace_watcher_service.py`
- [x] 3.2 Implement `start(openspec_root, on_change, workspace_service)` — creates asyncio task running the watch loop
- [x] 3.3 Implement debounce logic: collect events, reset timer on each new event, fire after 500ms quiescence
- [x] 3.4 Implement fingerprint comparison: re-read workspace, compare fingerprint with current, skip callback if same
- [x] 3.5 Implement `stop()` — cancel task, await cleanup, no-op if not started
- [x] 3.6 Wrap callback in try/except: log error and continue on exception
- [x] 3.7 Handle directory-deleted case: detect `FileNotFoundError` on re-read, stop watcher

## 4. Container wiring

- [x] 4.1 Add `create_workspace_watcher_service(workspace_service, observer)` to `Container` using `WatchfilesObserver` as default

## 5. App integration

- [x] 5.1 Start watcher in `OpsxTuiApp.on_mount()` after `_load_workspace()` completes
- [x] 5.2 Register callback that updates `self.opsx_project.workspace` with new snapshot and calls `refresh()` on current screen
- [x] 5.3 Stop watcher in `OpsxTuiApp.on_unmount()`

## 6. Fixtures

- [x] 6.1 Create `FakeWorkspaceObserver` in test fixtures that yields controlled path batches on demand
- [x] 6.2 Create temp directory fixture with minimal `openspec/` structure for integration tests

## 7. Tests

- [x] 7.1 Test `WorkspaceObserver` port contract with `FakeWorkspaceObserver`
- [x] 7.2 Test debounce: rapid events fire callback once after 500ms quiescence
- [x] 7.3 Test debounce: single event fires callback once
- [x] 7.4 Test fingerprint skip: temp file events do not trigger callback
- [x] 7.5 Test fingerprint skip: content change triggers callback
- [x] 7.6 Test start/stop lifecycle: stop cancels task, stop without start is no-op
- [x] 7.7 Test callback error: exception logged, watcher continues
- [x] 7.8 Test container creates watcher service with correct observer
- [x] 7.9 Integration test: real watchfiles + temp dir, events trigger callback
- [x] 7.10 Integration test: directory removal stops watcher

## 8. Quality verification

- [x] 8.1 Run `ruff check .` and fix issues
- [x] 8.2 Run `mypy src` and fix issues
- [x] 8.3 Verify all existing tests still pass