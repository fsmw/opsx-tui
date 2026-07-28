from __future__ import annotations

from opsx_tui.domain.openspec_cli import OpenSpecCLIInfo
from opsx_tui.domain.ports import OpenSpecCLIDetector


class OpenSpecCLIDetectionService:
    def __init__(self, detector: OpenSpecCLIDetector) -> None:
        self._detector = detector

    async def detect(self) -> OpenSpecCLIInfo:
        return await self._detector.detect()
