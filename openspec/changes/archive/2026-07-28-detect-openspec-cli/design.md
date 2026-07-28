# Design: Detect OpenSpec CLI

## D1 — OpenSpecCLIInfo frozen model

A single frozen Pydantic model carries all detection results. Optional fields
represent unknowns without None-guessing.

```python
class OpenSpecCLIInfo(BaseModel, frozen=True):
    path: Path | None = None
    version: str | None = None
    version_tuple: tuple[int, int, int] | None = None
    is_compatible: bool = False
    available_commands: frozenset[str] = frozenset()
    diagnostics: tuple[Diagnostic, ...] = ()
```

-   `path=None` when executable not found.
-   `version=None` when version query failed.
-   `is_compatible` is only True when `path` is set AND `version_tuple >= MINIMUM`.
-   `available_commands` may be empty if both detection methods fail.
-   `diagnostics` accumulates every failure reason.

## D2 — Async port from the start

Even though detection is a one-shot at startup, the port is async because
the next change (CLI command execution) will be async.

```python
class OpenSpecCLIDetector(Protocol):
    async def detect(self) -> OpenSpecCLIInfo: ...
```

Keeps the contract stable across Fase 4.

## D3 — Executable resolution via shutil.which

```python
path = shutil.which("openspec")
```

-   Pure stdlib, no new dependencies.
-   Respects PATH, handles executability.
-   Returns `None` → ERROR diagnostic, short-circuit (skip version/commands).

## D4 — Version query with asyncio.create_subprocess_exec

```python
proc = await asyncio.create_subprocess_exec(
    str(path), "--version",
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
)
stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
```

-   No `shell=True`, args as list.
-   Timeout via `asyncio.wait_for`.
-   Parse stdout with `re.search(r"(\d+)\.(\d+)\.(\d+)", stdout)`.
-   Non-zero exit, timeout, OSError → WARNING diagnostic, version=None.

## D5 — Semver minimum constant

```python
CLI_VERSION_MINIMUM = (0, 1, 0)
```

-   Defined in `domain/openspec_cli.py` alongside `OpenSpecCLIInfo`.
-   `is_compatible = version_tuple is not None and version_tuple >= CLI_VERSION_MINIMUM`.
-   If version is below minimum → WARNING diagnostic.

## D6 — Available commands via two-tier strategy

**Primary**: `openspec list --json` → parse JSON array of command names.

**Fallback**: `openspec --help` → extract section headers matching
`^  [a-z]` pattern (fragile but better than nothing).

**If both fail**: `available_commands` remains empty, WARNING diagnostic.

## D7 — Error handling per subprocess attempt

| Failure mode | Diagnostic level | Message |
|---|---|---|
| Executable not found | ERROR | "openspec CLI not found in PATH" |
| Version query timeout | WARNING | "openspec --version timed out after 10s" |
| Version query non-zero | WARNING | "openspec --version exited with code {rc}" |
| Version parse failed | WARNING | "Could not parse version from: {raw}" |
| Commands query failed | WARNING | "Could not list available commands" |
| Permission denied | ERROR | "openspec executable at {path} is not executable" |

## D8 — Architecture placement

```
domain/openspec_cli.py       → OpenSpecCLIInfo, CLI_VERSION_MINIMUM
domain/ports.py              → OpenSpecCLIDetector (Protocol)
infrastructure/cli_detector.py → ProcessOpenSpecCLIDetector
application/cli_detection_service.py → OpenSpecCLIDetectionService
application/container.py     → create_cli_detector(), run_cli_detection()
presentation/views/settings_view.py → CLI status section (placeholder)
presentation/app.py          → detection on load, state on OpsxTuiApp
```

## D9 — No persistence

Detection runs on every app startup and on workspace re-read. If the CLI is
installed mid-session the next workspace refresh picks it up. No TOML sidecar,
no SQLite — the detection is a live healthcheck, not a configuration value.
