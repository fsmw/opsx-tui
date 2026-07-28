from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path

from opsx_tui.application.workspace_service import WorkspaceService
from opsx_tui.domain.logging import Logger
from opsx_tui.domain.ports import WorkspaceObserver
from opsx_tui.domain.workspace import WorkspaceSnapshot


class WorkspaceWatcherService:
    def __init__(
        self,
        observer: WorkspaceObserver,
        logger: Logger,
        workspace_service: WorkspaceService,
    ) -> None:
        self._observer = observer
        self._logger = logger
        self._workspace_service = workspace_service
        self._task: asyncio.Task[None] | None = None
        self._openspec_root: Path | None = None
        self._current_fingerprint: str | None = None
        self._on_change: Callable[[WorkspaceSnapshot], None] | None = None

    def start(
        self,
        openspec_root: Path,
        on_change: Callable[[WorkspaceSnapshot], None],
    ) -> None:
        self._openspec_root = openspec_root
        self._on_change = on_change
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(self) -> None:
        root = self._openspec_root
        if root is None:
            return
        debounce_task: asyncio.Task[None] | None = None
        try:
            async for _ in self._observer.watch(root):
                if debounce_task is not None:
                    debounce_task.cancel()
                debounce_task = asyncio.create_task(self._debounce_and_fire())
        except FileNotFoundError:
            self._logger.warning(
                f"Watch directory deleted: {root!r}"
            )
        except OSError as e:
            self._logger.error(f"Fatal watch error on {root}: {e}")
        except asyncio.CancelledError:
            if debounce_task is not None:
                debounce_task.cancel()

    async def _debounce_and_fire(self) -> None:
        try:
            await asyncio.sleep(0.5)
            await self._fire()
        except asyncio.CancelledError:
            pass

    async def _fire(self) -> None:
        root = self._openspec_root
        if root is None:
            return
        try:
            snapshot = self._workspace_service.read_snapshot(root)
            if (
                self._current_fingerprint is not None
                and snapshot.fingerprint == self._current_fingerprint
            ):
                self._logger.debug("Fingerprint unchanged, skipping callback")
                return
            self._current_fingerprint = snapshot.fingerprint
            if self._on_change is not None:
                self._on_change(snapshot)
        except FileNotFoundError:
            self._logger.warning(
                f"Workspace not found during re-read: {root}"
            )
        except Exception:
            self._logger.error("Watcher re-read failed", exc_info=True)
