## 1. Background parsing implementation

- [x] 1.1 In `src/opsx_tui/application/workspace_watcher_service.py`, modify `_fire()` to execute `self._workspace_service.read_snapshot(root)` via `await asyncio.to_thread(...)`.
- [x] 1.2 In `src/opsx_tui/presentation/app.py`, change `on_mount` to `async def on_mount(self)` so it can await async operations.
- [x] 1.3 In `src/opsx_tui/presentation/app.py` within `_load_workspace()`, modify the synchronous call to `ws_service.read_snapshot(...)` to use `await asyncio.to_thread(...)` (this requires propagating `async` up to `_load_workspace` or handling it properly within `on_mount`).
