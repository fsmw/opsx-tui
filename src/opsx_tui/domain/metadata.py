from __future__ import annotations

from enum import IntEnum

from pydantic import BaseModel


class Priority(IntEnum):
    NORMAL = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class ChangeMetadata(BaseModel, frozen=True):
    priority: Priority = Priority.NORMAL
    tags: tuple[str, ...] = ()
    favorite: bool = False
    blocked_reason: str | None = None
    notes: str | None = None
    order: int = 0
