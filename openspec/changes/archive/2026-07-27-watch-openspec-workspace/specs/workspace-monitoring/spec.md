## ADDED Requirements

### Requirement: Workspace observer port
The system SHALL define a `WorkspaceObserver` Protocol in `domain/ports.py` with a `watch(path: Path) -> AsyncIterator[tuple[Path, ...]]` method. The iterator SHALL yield batches of paths that changed after each filesystem event batch.

#### Scenario: Observer yields path batches
- **WHEN** a `FakeWorkspaceObserver` yields `(Path("a.md"), Path("b.md"))`
- **THEN** the caller processes them as one batch

#### Scenario: Observer terminates on cancellation
- **WHEN** the consumer cancels the iteration
- **THEN** the observer stops cleanly (no leaked handles)

### Requirement: WatchfilesObserver adapter
The system SHALL implement a `WatchfilesObserver` in `infrastructure/` wrapping `watchfiles.awatch()` that watches only the `openspec/` directory recursively. It SHALL yield batches of changed paths.

#### Scenario: Watches openspec directory
- **WHEN** `WatchfilesObserver.watch(openspec_root)` is called
- **THEN** it calls `awatch(openspec_root / "openspec")` and yields changed paths

#### Scenario: Transient error does not stop iteration
- **WHEN** a transient filesystem error occurs (e.g., permission denied on a subdirectory)
- **THEN** the observer logs a warning and continues watching

### Requirement: WorkspaceWatcherService with debounce
The system SHALL implement `WorkspaceWatcherService` in `application/` with `start(openspec_root, on_change)` and `stop()` methods. It SHALL debounce filesystem events with a 500ms quiescence window.

#### Scenario: Debounce collects events in 500ms window
- **WHEN** events arrive at t=0ms, t=100ms, t=200ms
- **THEN** the callback is NOT invoked at t=100ms, t=200ms; only once after t=700ms (500ms after the last event)

#### Scenario: Single event triggers callback
- **WHEN** one file changes and no other events arrive within 500ms
- **THEN** the callback is invoked once with the new snapshot

#### Scenario: No events = no callback
- **WHEN** no files change
- **THEN** the callback is never invoked

### Requirement: Fingerprint comparison skips re-read
Before re-reading the workspace, the watcher SHALL compute a lightweight fingerprint and compare it with the current snapshot's fingerprint. If fingerprints match, the callback SHALL NOT be invoked.

#### Scenario: Temp file creation does not trigger re-read
- **WHEN** a temp file (e.g., `temp.md~`) is created and deleted inside `openspec/`
- **THEN** the fingerprint does not change and the callback is NOT invoked

#### Scenario: Content change triggers re-read
- **WHEN** a spec file's content changes
- **THEN** the fingerprint changes and the callback IS invoked with a new snapshot

### Requirement: Clean start/stop lifecycle
`start()` SHALL create an asyncio task running the watch loop. `stop()` SHALL cancel the task and await cleanup. Calling `stop()` when not started SHALL be a no-op.

#### Scenario: Stop cancels the watch task
- **WHEN** `start()` is called, then `stop()` is called within 100ms
- **THEN** no callback is ever invoked and no resources leak

#### Scenario: Stop without start is no-op
- **WHEN** `stop()` is called without a prior `start()`
- **THEN** no error is raised

### Requirement: Error resilience
The watcher SHALL handle errors gracefully: transient filesystem errors (permission, not-found) SHALL be logged and the watcher SHALL continue. An unhandled exception in the callback SHALL be logged and the watcher SHALL continue. Critical errors (e.g., watched directory deleted) SHALL stop the watcher.

#### Scenario: Callback error does not crash watcher
- **WHEN** the `on_change` callback raises an exception
- **THEN** the watcher logs the error and continues watching

#### Scenario: Directory deleted stops watcher
- **WHEN** the watched `openspec/` directory is deleted
- **THEN** the watcher stops and logs the reason

### Requirement: Container wiring
The `Container` SHALL provide `create_workspace_watcher_service(workspace_service, observer)` using `WatchfilesObserver` as the default observer.

#### Scenario: Container creates watcher service
- **WHEN** `container.create_workspace_watcher_service(workspace_service, observer)` is called
- **THEN** a `WorkspaceWatcherService` is returned with the given observer

### Requirement: App integration
`OpsxTuiApp` SHALL start the watcher in `on_mount()` after `_load_workspace()` completes, and SHALL stop it in `on_unmount()`. The callback SHALL update `self.opsx_project` and call `refresh()` on the current screen.

#### Scenario: Watcher starts after workspace load
- **WHEN** the app mounts and loads the workspace successfully
- **THEN** the watcher is started on the project's `openspec_root`

#### Scenario: Watcher updates the project on change
- **WHEN** the watcher callback fires with a new snapshot
- **THEN** `self.opsx_project.workspace` is updated to the new snapshot

#### Scenario: Watcher stops on unmount
- **WHEN** the app unmounts
- **THEN** the watcher is stopped cleanly