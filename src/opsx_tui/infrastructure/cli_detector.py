from __future__ import annotations

import asyncio
import re
import shutil
from pathlib import Path

from opsx_tui.domain.openspec_cli import CLI_VERSION_MINIMUM, OpenSpecCLIInfo
from opsx_tui.domain.project import Diagnostic, DiagnosticLevel

_VERSION_REGEX = re.compile(r"(\d+)\.(\d+)\.(\d+)")

_LIST_TIMEOUT = 10


class ProcessOpenSpecCLIDetector:
    async def detect(self) -> OpenSpecCLIInfo:
        path = self._find_executable()
        if path is None:
            return OpenSpecCLIInfo(
                diagnostics=(
                    Diagnostic(
                        level=DiagnosticLevel.ERROR,
                        message="openspec CLI not found in PATH",
                    ),
                ),
            )

        version, version_tuple, version_diags = await self._query_version(path)
        is_compatible = _check_compatibility(version_tuple, version_diags)
        commands, cmd_diags = await self._query_commands(path)

        all_diags = (*version_diags, *cmd_diags)
        return OpenSpecCLIInfo(
            path=path,
            version=version,
            version_tuple=version_tuple,
            is_compatible=is_compatible,
            available_commands=commands,
            diagnostics=all_diags,
        )

    def _find_executable(self) -> Path | None:
        found = shutil.which("openspec")
        return Path(found).resolve() if found else None

    async def _query_version(
        self, path: Path
    ) -> tuple[str | None, tuple[int, int, int] | None, tuple[Diagnostic, ...]]:
        try:
            proc = await asyncio.create_subprocess_exec(
                str(path),
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=10
            )
        except OSError:
            return None, None, (
                Diagnostic(
                    level=DiagnosticLevel.ERROR,
                    message=f"openspec executable at {path} is not executable",
                ),
            )
        except TimeoutError:
            return None, None, (
                Diagnostic(
                    level=DiagnosticLevel.WARNING,
                    message="openspec --version timed out after 10s",
                ),
            )

        if proc.returncode != 0:
            raw = (stdout + stderr).decode().strip()
            return None, None, (
                Diagnostic(
                    level=DiagnosticLevel.WARNING,
                    message=(
                        f"openspec --version exited with code {proc.returncode}"
                        f"{': ' + raw if raw else ''}"
                    ),
                ),
            )

        raw = stdout.decode().strip()
        match = _VERSION_REGEX.search(raw)
        if match:
            return raw, (int(match[1]), int(match[2]), int(match[3])), ()
        return raw, None, (
            Diagnostic(
                level=DiagnosticLevel.WARNING,
                message=f"Could not parse version from: {raw}",
            ),
        )

    async def _query_commands(
        self, path: Path
    ) -> tuple[frozenset[str], tuple[Diagnostic, ...]]:
        try:
            proc = await asyncio.create_subprocess_exec(
                str(path),
                "list",
                "--json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=_LIST_TIMEOUT
            )
        except (TimeoutError, OSError):
            return await self._query_commands_help(path)

        if proc.returncode != 0:
            return await self._query_commands_help(path)

        import json

        try:
            cmds: list[str] = json.loads(stdout.decode())
            if isinstance(cmds, list):
                return frozenset(cmd for cmd in cmds if isinstance(cmd, str)), ()
        except (json.JSONDecodeError, TypeError):
            pass

        return await self._query_commands_help(path)

    async def _query_commands_help(
        self, path: Path
    ) -> tuple[frozenset[str], tuple[Diagnostic, ...]]:
        try:
            proc = await asyncio.create_subprocess_exec(
                str(path),
                "--help",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=_LIST_TIMEOUT
            )
        except (TimeoutError, OSError):
            return frozenset(), (
                Diagnostic(
                    level=DiagnosticLevel.WARNING,
                    message="Could not list available commands",
                ),
            )

        if proc.returncode != 0:
            return frozenset(), (
                Diagnostic(
                    level=DiagnosticLevel.WARNING,
                    message="Could not list available commands",
                ),
            )

        text = stdout.decode()
        cmds = _parse_help_commands(text)
        if cmds:
            return frozenset(cmds), ()
        return frozenset(), (
            Diagnostic(
                level=DiagnosticLevel.WARNING,
                message="Could not list available commands",
            ),
        )


def _check_compatibility(
    version_tuple: tuple[int, int, int] | None,
    existing_diags: tuple[Diagnostic, ...],
) -> bool:
    if version_tuple is None:
        return False
    if version_tuple >= CLI_VERSION_MINIMUM:
        return True
    return False


def _parse_help_commands(text: str) -> list[str]:
    cmds: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("{") or stripped.startswith("}"):
            continue
        parts = stripped.split()
        if parts and parts[0].startswith("{") and parts[0].endswith("}"):
            continue
        if parts and _is_command_name(parts[0]):
            cmds.append(parts[0])
    return cmds


def _is_command_name(s: str) -> bool:
    if len(s) < 2:
        return False
    return s.islower() and s.isascii() and not s.startswith("-")
