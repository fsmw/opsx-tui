from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from opsx_tui.infrastructure.cli_detector import (
    ProcessOpenSpecCLIDetector,
    _check_compatibility,
    _parse_help_commands,
)


class TestCheckCompatibility:
    def test_meets_minimum(self) -> None:
        assert _check_compatibility((0, 1, 0), ()) is True

    def test_above_minimum(self) -> None:
        assert _check_compatibility((0, 2, 1), ()) is True

    def test_below_minimum(self) -> None:
        assert _check_compatibility((0, 0, 9), ()) is False

    def test_none_version(self) -> None:
        assert _check_compatibility(None, ()) is False


class TestParseHelpCommands:
    def test_empty_output(self) -> None:
        assert _parse_help_commands("") == []

    def test_help_text(self) -> None:
        text = (
            "Usage: openspec [OPTIONS] COMMAND\n\n"
            "  list     List changes or specs\n"
            "  new      Create a new change\n"
            "  status   Show change status\n"
        )
        cmds = _parse_help_commands(text)
        assert "list" in cmds
        assert "new" in cmds
        assert "status" in cmds

    def test_skips_flags(self) -> None:
        text = "  --help   Show help\n  -v       Verbose\n  list     List items\n"
        cmds = _parse_help_commands(text)
        assert "list" in cmds
        assert "--help" not in cmds


class TestProcessOpenSpecCLIDetector:
    async def test_missing_executable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "opsx_tui.infrastructure.cli_detector.shutil.which",
            lambda _: None,
        )
        detector = ProcessOpenSpecCLIDetector()
        info = await detector.detect()
        assert info.path is None
        assert info.is_compatible is False
        assert any("not found" in d.message.lower() for d in info.diagnostics)

    async def test_version_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        async def _fake_create_subprocess_exec(*args: object, **kw: object) -> object:
            class FakeProcess:
                returncode = 0

                async def communicate(self) -> tuple[bytes, bytes]:
                    await asyncio.sleep(999)

            return FakeProcess()

        monkeypatch.setattr(
            "opsx_tui.infrastructure.cli_detector.shutil.which",
            lambda _: Path("/usr/bin/openspec"),
        )
        monkeypatch.setattr(
            "asyncio.create_subprocess_exec", _fake_create_subprocess_exec
        )

        detector = ProcessOpenSpecCLIDetector()
        import asyncio as asyncio_mod

        orig_wait = asyncio_mod.wait_for

        async def short_timeout(coro: object, timeout: object) -> object:
            return await orig_wait(coro, timeout=0.001)

        monkeypatch.setattr("asyncio.wait_for", short_timeout)
        info = await detector.detect()
        assert info.version is None
        assert info.is_compatible is False

    async def test_version_non_zero_exit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        async def _fake_create_subprocess_exec(*args: object, **kw: object) -> object:
            class FakeProcess:
                returncode = 1

                async def communicate(self) -> tuple[bytes, bytes]:
                    return b"", b"error"

            return FakeProcess()

        monkeypatch.setattr(
            "opsx_tui.infrastructure.cli_detector.shutil.which",
            lambda _: Path("/usr/bin/openspec"),
        )
        monkeypatch.setattr(
            "asyncio.create_subprocess_exec", _fake_create_subprocess_exec
        )
        detector = ProcessOpenSpecCLIDetector()
        info = await detector.detect()
        assert info.version is None
        assert info.is_compatible is False

    async def test_version_unparseable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        async def _fake_create_subprocess_exec(*args: object, **kw: object) -> object:
            class FakeProcess:
                returncode = 0

                async def communicate(self) -> tuple[bytes, bytes]:
                    return b"openspec development", b""

            return FakeProcess()

        monkeypatch.setattr(
            "opsx_tui.infrastructure.cli_detector.shutil.which",
            lambda _: Path("/usr/bin/openspec"),
        )
        monkeypatch.setattr(
            "asyncio.create_subprocess_exec", _fake_create_subprocess_exec
        )
        detector = ProcessOpenSpecCLIDetector()
        info = await detector.detect()
        assert info.version == "openspec development"
        assert info.version_tuple is None
        assert info.is_compatible is False
        assert any("parse" in d.message for d in info.diagnostics)

    async def test_successful_detection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        async def _fake_create_subprocess_exec(*args: object, **kw: object) -> object:
            cmd = args[1] if len(args) > 1 else ""
            class FakeProcess:
                returncode = 0

                async def communicate(self) -> tuple[bytes, bytes]:
                    if cmd == "--version":
                        return b"openspec 0.2.1", b""
                    if cmd == "list":
                        return b'["new","status","validate"]', b""
                    return b"", b""

            return FakeProcess()

        monkeypatch.setattr(
            "opsx_tui.infrastructure.cli_detector.shutil.which",
            lambda _: Path("/usr/bin/openspec"),
        )
        monkeypatch.setattr(
            "asyncio.create_subprocess_exec", _fake_create_subprocess_exec
        )
        detector = ProcessOpenSpecCLIDetector()
        info = await detector.detect()
        assert info.path == Path("/usr/bin/openspec")
        assert info.version == "openspec 0.2.1"
        assert info.version_tuple == (0, 2, 1)
        assert info.is_compatible is True
        assert "new" in info.available_commands
