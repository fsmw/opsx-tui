from __future__ import annotations

from opsx_tui.domain.metadata import ChangeMetadata
from opsx_tui.domain.workspace import Change, WorkspaceSnapshot


def merge_metadata(
    snapshot: WorkspaceSnapshot,
    metadata_map: dict[str, ChangeMetadata],
) -> WorkspaceSnapshot:
    def _merge(changes: tuple[Change, ...]) -> tuple[Change, ...]:
        return tuple(
            change.model_copy(update={"metadata": metadata_map.get(change.name)})
            for change in changes
        )

    return snapshot.model_copy(
        update={
            "active_changes": _merge(snapshot.active_changes),
            "archived_changes": _merge(snapshot.archived_changes),
        }
    )
