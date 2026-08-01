from __future__ import annotations

from enum import StrEnum


class ChangeStatus(StrEnum):
    DRAFT = "draft"
    PLANNING = "planning"
    READY = "ready"
    APPLYING = "applying"
    VERIFICATION = "verification"
    READY_TO_ARCHIVE = "ready-to-archive"
    BLOCKED = "blocked"
    ARCHIVED = "archived"
    UNKNOWN = "unknown"
