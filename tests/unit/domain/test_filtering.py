from __future__ import annotations

from pathlib import Path

from opsx_tui.domain.change_parser import ParsedTaskList
from opsx_tui.domain.filtering import ChangeFilter, filter_changes
from opsx_tui.domain.metadata import ChangeMetadata
from opsx_tui.domain.status import ChangeStatus
from opsx_tui.domain.workspace import Change


def _make_change(
    name: str,
    state: ChangeStatus = ChangeStatus.READY,
    is_archived: bool = False,
    tags: tuple[str, ...] = (),
) -> Change:
    metadata = ChangeMetadata(tags=tags) if tags else None
    return Change(
        name=name,
        change_dir=Path(name),
        absolute_change_dir=Path(f"/test/{name}"),
        artifacts=(),
        is_archived=is_archived,
        state=state,
        parsed_tasks=ParsedTaskList(
            items=(), total=0, completed=0, section_map={}, diagnostics=()
        ),
        metadata=metadata,
    )


CHANGES = (
    _make_change("alpha", state=ChangeStatus.READY),
    _make_change("beta", state=ChangeStatus.APPLYING, tags=("ui",)),
    _make_change(
        "gamma",
        state=ChangeStatus.READY,
        is_archived=True,
        tags=("ui", "core"),
    ),
    _make_change("delta", state=ChangeStatus.BLOCKED, tags=("core",)),
)


def test_state_filter_single_state() -> None:
    filt = ChangeFilter(states=frozenset({ChangeStatus.READY}))
    result = filter_changes(CHANGES, filt)
    assert {c.name for c in result} == {"alpha"}


def test_state_filter_multi_state() -> None:
    filt = ChangeFilter(states=frozenset({ChangeStatus.READY, ChangeStatus.BLOCKED}))
    result = filter_changes(CHANGES, filt)
    assert {c.name for c in result} == {"alpha", "delta"}


def test_state_filter_empty_means_all() -> None:
    result = filter_changes(CHANGES, ChangeFilter())
    assert len(result) == 3  # archived excluded by default


def test_text_filter_substring() -> None:
    result = filter_changes(CHANGES, ChangeFilter(text="ha"))
    assert {c.name for c in result} == {"alpha"}


def test_text_filter_case_insensitive() -> None:
    result = filter_changes(CHANGES, ChangeFilter(text="ALPH"))
    assert {c.name for c in result} == {"alpha"}


def test_text_filter_empty_shows_all() -> None:
    result = filter_changes(CHANGES, ChangeFilter(text=""))
    assert len(result) == 3


def test_tag_filter_single() -> None:
    result = filter_changes(CHANGES, ChangeFilter(tags=("ui",)))
    assert {c.name for c in result} == {"beta"}


def test_tag_filter_multiple_requires_all() -> None:
    filt = ChangeFilter(tags=("ui", "core"), include_archived=True)
    result = filter_changes(CHANGES, filt)
    assert {c.name for c in result} == {"gamma"}


def test_tag_filter_no_metadata_never_matches() -> None:
    result = filter_changes(CHANGES, ChangeFilter(tags=("core",)))
    assert {c.name for c in result} == {"delta"}


def test_archived_hidden_by_default() -> None:
    result = filter_changes(CHANGES, ChangeFilter())
    assert not any(c.is_archived for c in result)


def test_archived_included_when_toggled() -> None:
    result = filter_changes(CHANGES, ChangeFilter(include_archived=True))
    assert {c.name for c in result} == {"alpha", "beta", "gamma", "delta"}


def test_combined_state_and_text() -> None:
    filt = ChangeFilter(states=frozenset({ChangeStatus.READY}), text="ha")
    result = filter_changes(CHANGES, filt)
    assert {c.name for c in result} == {"alpha"}


def test_combined_state_text_tag() -> None:
    filt = ChangeFilter(
        states=frozenset({ChangeStatus.READY}),
        text="ga",
        tags=("core",),
        include_archived=True,
    )
    result = filter_changes(CHANGES, filt)
    assert {c.name for c in result} == {"gamma"}


def test_is_active_truth_table() -> None:
    assert not ChangeFilter().is_active()
    assert ChangeFilter(states=frozenset({ChangeStatus.READY})).is_active()
    assert ChangeFilter(text="x").is_active()
    assert ChangeFilter(tags=("ui",)).is_active()
    assert ChangeFilter(include_archived=True).is_active()


def test_filter_preserves_order() -> None:
    source = (
        _make_change("zebra"),
        _make_change("alpha"),
        _make_change("mango"),
    )
    result = filter_changes(source, ChangeFilter())
    assert [c.name for c in result] == ["zebra", "alpha", "mango"]


def test_filter_never_mutates_input() -> None:
    import copy

    source = list(CHANGES)
    before = copy.deepcopy(source)
    filter_changes(source, ChangeFilter(include_archived=True, text="a"))
    assert [c.name for c in before] == [c.name for c in source]
    assert [c.state for c in before] == [c.state for c in source]
