from __future__ import annotations

from pathlib import Path

from opsx_tui.domain.change_parser import ParsedTaskList
from opsx_tui.domain.metadata import ChangeMetadata, Priority
from opsx_tui.domain.status import ChangeStatus
from opsx_tui.domain.workspace import ArtifactInfo, ArtifactKind, Change
from opsx_tui.presentation.views.change_formatting import (
    artifact_icons,
    format_change_item,
    format_progress,
    metadata_prefix,
    state_abbrev,
)


def _make_change(
    name: str,
    state: ChangeStatus = ChangeStatus.APPLYING,
    metadata: ChangeMetadata | None = None,
    artifacts: tuple[ArtifactInfo, ...] = (),
    tasks: ParsedTaskList | None = None,
) -> Change:
    return Change(
        name=name,
        change_dir=Path(name),
        absolute_change_dir=Path(f"/test/{name}"),
        artifacts=artifacts,
        is_archived=False,
        state=state,
        parsed_tasks=tasks,
        metadata=metadata,
    )


def _artifact(kind: ArtifactKind, exists: bool) -> ArtifactInfo:
    return ArtifactInfo(
        kind=kind,
        path=Path(f"{kind.value}.md"),
        absolute_path=Path(f"/test/{kind.value}.md"),
        exists=exists,
    )


def _tasks(completed: int, total: int) -> ParsedTaskList:
    return ParsedTaskList(
        items=(),
        total=total,
        completed=completed,
        section_map={},
        diagnostics=(),
    )


def test_state_abbrev_all_states() -> None:
    expected = {
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
    for value, abbr in expected.items():
        assert state_abbrev(value) == abbr


def test_format_progress_renders_completed_total() -> None:
    assert format_progress(_tasks(3, 7)) == "3/7"


def test_format_progress_zero_tasks_returns_no_tasks() -> None:
    assert format_progress(_tasks(0, 0)) == "no tasks"


def test_format_progress_none_returns_no_tasks() -> None:
    assert format_progress(None) == "no tasks"


def test_format_progress_never_renders_percent() -> None:
    assert "%" not in format_progress(_tasks(7, 7))


def test_metadata_prefix_urgent() -> None:
    change = _make_change("c", metadata=ChangeMetadata(priority=Priority.URGENT))
    assert "[U]" in metadata_prefix(change)


def test_metadata_prefix_high() -> None:
    change = _make_change("c", metadata=ChangeMetadata(priority=Priority.HIGH))
    assert "[H]" in metadata_prefix(change)


def test_metadata_prefix_normal_no_priority_marker() -> None:
    change = _make_change("c", metadata=ChangeMetadata(priority=Priority.NORMAL))
    assert "[U]" not in metadata_prefix(change)
    assert "[H]" not in metadata_prefix(change)


def test_metadata_prefix_favorite() -> None:
    change = _make_change("c", metadata=ChangeMetadata(favorite=True))
    assert "\u2605" in metadata_prefix(change)


def test_metadata_prefix_tag_truncated() -> None:
    change = _make_change(
        "c", metadata=ChangeMetadata(tags=("a-very-long-tag-name",))
    )
    prefix = metadata_prefix(change)
    assert "a-very-lo" in prefix
    assert "a-very-long-tag-name" not in prefix


def test_metadata_prefix_no_metadata_empty() -> None:
    assert metadata_prefix(_make_change("c")) == ""


def test_artifact_icons_marks_present_and_missing() -> None:
    artifacts = (
        _artifact(ArtifactKind.PROPOSAL, True),
        _artifact(ArtifactKind.DESIGN, False),
        _artifact(ArtifactKind.TASKS, True),
    )
    icons = artifact_icons(_make_change("c", artifacts=artifacts))
    assert "\u2713proposal" in icons
    assert "\u2717design" in icons
    assert "\u2713tasks" in icons


def test_artifact_icons_empty() -> None:
    assert artifact_icons(_make_change("c")) == ""


def test_format_change_item_contains_name_state_progress() -> None:
    change = _make_change(
        "add-feature",
        state=ChangeStatus.PLANNING,
        tasks=_tasks(2, 5),
    )
    text = format_change_item(change)
    assert "add-feature" in text
    assert "PLN" in text
    assert "2/5" in text


def test_format_change_item_no_tasks_no_progress() -> None:
    change = _make_change("bare")
    text = format_change_item(change)
    assert "no tasks" not in text
    assert "/" not in text.replace("[U]", "").replace("[H]", "")
