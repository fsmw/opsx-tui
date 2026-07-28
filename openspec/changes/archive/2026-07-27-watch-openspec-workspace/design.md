## Context

The app loads the workspace once at startup via `WorkspaceService.read_snapshot()`. This returns an immutable `WorkspaceSnapshot` with a `fingerprint` (SHA256 of directory contents). The app stores this in `OpenSpecProject(project=..., workspace=...)`.

The change adds reactive watching so the snapshot updates when the filesystem changes. The watcher must integrate with existing components:
- `WorkspaceService` (used to re-read)
- `WorkspaceSnapshot.fingerprint` (compare before/after)
- `Container` (wire the watcher)
- `OpsxTuiApp` (start/stop the watcher)

## Goals / Non-Goals

**Goals:**
- Watch `openspec/` directory recursively for create/modify/delete/move events via watchfiles.
- Debounce rapid events (500ms quiescence window).
- Re-read workspace only if fingerprint changed (avoid re-read on temp files, no-op edits).
- Callback-based notification of new snapshots (no direct Textual dependency).
- Clean start/stop lifecycle (cancel asyncio task, no leaked resources).
- Resilience: log transient errors, stop on critical errors.
- Testable: debounce logic testable in isolation, observer swappable in tests.

**Non-Goals:**
- Incremental diff of workspace (full re-read always; comparing snapshots is a separate concern).
- Automatic re-rendering of UI (the app callback handles that; this change provides the new snapshot).
- Polling fallback (watchfiles handles all platforms; add later if needed).
- Multi-project watching (one watcher per project workspace; future change if needed).

## Decisions

### D1: WorkspaceObserver Protocol in domain
**Choice:** Define `WorkspaceObserver` as an `AsyncIterator[tuple[Path, ...]]` Protocol in `domain/ports.py`.
**Why:** Established pattern (see `ConfigLoader`, `WorkspaceReader`). Makes the watcher service testable without real inotify. Allows a `FakeWorkspaceObserver` in tests.
**Alternatives:** No port, use watchfiles directly in the service — rejected because it couples the service to infrastructure and makes tests fragile.

```python
class WorkspaceObserver(Protocol):
    async def watch(self, path: Path) -> AsyncIterator[tuple[Path, ...]]: ...
```

### D2: Watch only `openspec/` directory
**Choice:** Watch `openspec/` under the project root, not the entire project tree.
**Why:** This is the only directory the app reads. Watching wider wastes CPU and generates irrelevant events (e.g., `__pycache__/`, `.git/`, source files).
**Alternatives:** Watch project root with ignore patterns — rejected as more complex and error-prone. `openspec/` is the single source of truth.

### D3: Debounce in application layer
**Choice:** `WorkspaceWatcherService` owns debounce logic. The observer yields individual event batches; the service collects them and waits for a 500ms quiescence window before triggering a re-read.
**Why:** Keeps infrastructure thin (just wrap `awatch()`). Debounce is an application concern. Testable with fake observer.
**Alternatives:** Debounce in infrastructure — rejected because it couples infra to timing concerns, making tests harder.

Debounce algorithm:
```
collect events → start timer (500ms) → more events arrive? → reset timer → timer fires → evaluate
```

### D4: Fingerprint comparison to avoid unnecessary re-reads
**Choice:** Before re-reading, check if the existing `WorkspaceSnapshot.fingerprint` matches the expected new fingerprint by doing a lightweight stat scan first.
**Why:** Not all filesystem events change workspace content (temp files, `*~`, `.swp`, directory metadata). The fingerprint is fast to compute (SHA256 of sorted paths + mtimes).
**Alternatives:** Always re-read — simpler but wasteful for high-event scenarios like editor auto-saves.

### D5: Callback-based notification
**Choice:** `WorkspaceWatcherService.watch(openspec_root, callback)` where `callback(snapshot: WorkspaceSnapshot) -> None`. The app registers `self._on_workspace_change` which updates `self.opsx_project` and calls `refresh` on the current screen.
**Why:** Decouples watcher from Textual. The app can decide what to do with the new snapshot.
**Alternatives:** Textual `post_message` — rejected because it ties the service to the framework. Async queue — over-engineered for single-consumer.

### D6: Separate start/stop lifecycle
**Choice:** `start()` creates an asyncio task running the watch loop. `stop()` cancels the task and awaits cleanup. The app calls `start()` in `on_mount()` after `_load_workspace`, and `stop()` in `on_unmount()`.
**Why:** Explicit lifecycle matches the asyncio pattern. No surprises. Works with Textual's worker pool.
**Alternatives:** Context manager (`async with`) — incompatible with long-lived app lifecycle. Implicit start on first yield — less clear.

### D7: No port for debounce/testability via fake observer
**Choice:** Test debounce logic by plugging a `FakeWorkspaceObserver` that yields paths at controlled intervals. Test the callback receives the correct snapshots. Test fingerprint skip logic.
**Why:** `FakeWorkspaceObserver` is simpler than mocking watchfiles. The observer port makes the service testable at unit level.
**Alternatives:** Mock `watchfiles.awatch` — rejected as implementation-coupled. Integration tests with real temp dirs — acceptable for contract/acceptance level.

## Risks / Trade-offs

- **[Risk] watchfiles on non-Linux platforms** → watchfiles supports Linux (inotify), macOS (FSEvents), Windows (ReadDirectoryChangesW). Already declared in deps.
- **[Risk] High event volume during `openspec archive` or `openspec apply`** → Debounce (500ms) handles bursts. Fingerprint check prevents re-read if only metadata changed. The app only loads the `openspec/` subtree (~100 files max), so each re-read is fast (<50ms).
- **[Risk] Watcher fires during file write (partial content)** → Text editors typically write to temp → atomic rename, or truncate + write. In either case, the final settled state is caught by the next debounce window. The fingerprint check reads file contents if mtimes changed, ensuring consistent state.
- **[Risk] Race: watcher triggers re-read while agent is mid-write** → The fingerprint is computed from final file contents after the debounce window. If an agent is in the middle of writing, the mtimes change, triggering another event → another debounce → another re-read. Eventually settles.
- **[Risk] Callback throws** → The watcher wraps the callback in try/except. An exception logs and continues; the watcher does not crash.