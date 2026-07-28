from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path


class FakeWorkspaceObserver:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[tuple[Path, ...]] = asyncio.Queue()
        self.started: bool = False

    async def watch(self, path: Path) -> AsyncIterator[tuple[Path, ...]]:
        self.started = True
        try:
            while True:
                paths = await self._queue.get()
                yield paths
        except GeneratorExit:
            pass

    async def notify(self, *paths: Path) -> None:
        await self._queue.put(paths)
