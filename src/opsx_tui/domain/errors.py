from __future__ import annotations

from pathlib import Path


class ConfigLoadError(Exception):
    def __init__(self, path: Path, cause: Exception) -> None:
        self.path = path
        self.cause = cause
        super().__init__(f"Failed to load config from {path}: {cause}")


class WorkspaceReadError(Exception):
    def __init__(self, path: Path, reason: str) -> None:
        self.path = path
        self.reason = reason
        super().__init__(f"Failed to read workspace at {path}: {reason}")
