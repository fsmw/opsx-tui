from __future__ import annotations

from opsx_tui.domain.change_parser import ParsedTaskList
from opsx_tui.domain.metadata import Priority
from opsx_tui.domain.workspace import Change

_STATE_ABBREV: dict[str, str] = {
    "draft": "DFT",
    "planning": "PLN",
    "ready": "RDY",
    "applying": "APY",
    "verification": "VER",
    "ready-to-archive": "RTA",
    "blocked": "BLK",
    "archived": "ARC",
    "unknown": "UNK",
}


def state_abbrev(state_value: str) -> str:
    return _STATE_ABBREV.get(state_value, state_value.upper()[:3])


def format_progress(parsed_tasks: ParsedTaskList | None) -> str:
    if parsed_tasks is None or parsed_tasks.total == 0:
        return "no tasks"
    return f"{parsed_tasks.completed}/{parsed_tasks.total}"


def metadata_prefix(change: Change) -> str:
    meta = change.metadata
    prefix = ""
    if meta:
        if meta.priority >= Priority.HIGH:
            prefix += f"[{'U' if meta.priority == 4 else 'H'}]"
        if meta.favorite:
            prefix += "\u2605 "
        if meta.tags:
            prefix += f"[{meta.tags[0][:10]}] "
    return prefix


def artifact_icons(change: Change) -> str:
    artifacts_present: list[str] = []
    artifacts_missing: list[str] = []
    for a in change.artifacts:
        if a.exists:
            artifacts_present.append(a.kind.value)
        else:
            artifacts_missing.append(a.kind.value)
    icons = ""
    if artifacts_present:
        icons += "".join(f"\u2713{a}" for a in artifacts_present)
    if artifacts_missing:
        icons += "".join(f"\u2717{a}" for a in artifacts_missing)
    return icons


def format_change_item(change: Change) -> str:
    state_str = state_abbrev(change.state.value)
    prog = ""
    if change.parsed_tasks is not None:
        prog = f" {format_progress(change.parsed_tasks)}"
    prefix = metadata_prefix(change)
    icons = artifact_icons(change)
    return f"{prefix}[{state_str}]{prog} {change.name} {icons}"
