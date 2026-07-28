from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

from watchfiles import awatch

from opsx_tui.domain.logging import Logger


class WatchfilesObserver:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    async def watch(self, path: Path) -> AsyncIterator[tuple[Path, ...]]:
        watch_path = path / "openspec"
        async for changes in awatch(watch_path):
            yield tuple(Path(c[1]) for c in changes)
