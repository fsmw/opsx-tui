from __future__ import annotations

from pathlib import Path

from opsx_tui.domain.openspec_cli import OpenSpecCLIInfo
from opsx_tui.domain.project import Diagnostic, DiagnosticLevel


class FakeOpenSpecCLIDetector:
    def __init__(
        self,
        path: Path | None = Path("/usr/local/bin/openspec"),
        version: str | None = "0.2.1",
        version_tuple: tuple[int, int, int] | None = (0, 2, 1),
        is_compatible: bool = True,
        available_commands: frozenset[str] | None = None,
        diagnostics: tuple[Diagnostic, ...] = (),
        fail_detect: bool = False,
    ) -> None:
        self._info = OpenSpecCLIInfo(
            path=path,
            version=version,
            version_tuple=version_tuple,
            is_compatible=is_compatible,
            available_commands=(
                available_commands or frozenset({"new", "status", "validate"})
            ),
            diagnostics=diagnostics,
        )
        self._fail_detect = fail_detect

    async def detect(self) -> OpenSpecCLIInfo:
        if self._fail_detect:
            return OpenSpecCLIInfo(
                diagnostics=(
                    Diagnostic(
                        level=DiagnosticLevel.ERROR,
                        message="openspec CLI not found in PATH",
                    ),
                ),
            )
        return self._info
