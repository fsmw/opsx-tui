from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from pydantic import BaseModel

from opsx_tui.domain.status import ChangeStatus

if TYPE_CHECKING:
    from opsx_tui.domain.workspace import Change


class ChangeFilter(BaseModel, frozen=True):
    """Presentational filter applied over a set of changes.

    Pure filter model — never mutates changes and never touches canonical
    OpenSpec data. Empty states means "all states".
    """

    states: frozenset[ChangeStatus] = frozenset()
    text: str = ""
    tags: tuple[str, ...] = ()
    include_archived: bool = False

    def is_active(self) -> bool:
        return bool(self.states) or bool(self.text) or bool(self.tags) or (
            self.include_archived
        )


def filter_changes(changes: Iterable[Change], filt: ChangeFilter) -> tuple[Change, ...]:
    """Return the changes matching every active criterion in ``filt``.

    Rules are AND-ed: a change must satisfy all of them to be kept. The input
    order is preserved and no change is mutated.
    """

    def matches(change: Change) -> bool:
        if not filt.include_archived and change.is_archived:
            return False
        if filt.states and change.state not in filt.states:
            return False
        if filt.text and filt.text.lower() not in change.name.lower():
            return False
        if filt.tags:
            meta_tags = change.metadata.tags if change.metadata else ()
            if not all(tag in meta_tags for tag in filt.tags):
                return False
        return True

    return tuple(change for change in changes if matches(change))
