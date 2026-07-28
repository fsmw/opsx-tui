from __future__ import annotations

from pathlib import Path

from opsx_tui.application.cli_detection_service import OpenSpecCLIDetectionService
from tests.fixtures.cli_detection.fake_detector import FakeOpenSpecCLIDetector


class TestOpenSpecCLIDetectionService:
    async def test_detect_returns_info(self) -> None:
        detector = FakeOpenSpecCLIDetector(
            path=Path("/usr/bin/openspec"),
            version="0.2.1",
            version_tuple=(0, 2, 1),
            is_compatible=True,
        )
        service = OpenSpecCLIDetectionService(detector)
        info = await service.detect()
        assert info.path == Path("/usr/bin/openspec")
        assert info.version == "0.2.1"
        assert info.is_compatible is True

    async def test_detect_without_cli(self) -> None:
        detector = FakeOpenSpecCLIDetector(fail_detect=True)
        service = OpenSpecCLIDetectionService(detector)
        info = await service.detect()
        assert info.path is None
        assert info.is_compatible is False
