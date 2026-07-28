from __future__ import annotations

from pathlib import Path

import pytest

from opsx_tui.domain.metadata import ChangeMetadata, Priority
from opsx_tui.domain.workspace import Change, ChangeState


class TestPriorityEnum:
    def test_values(self) -> None:
        assert Priority.NORMAL.value == 0
        assert Priority.LOW.value == 1
        assert Priority.MEDIUM.value == 2
        assert Priority.HIGH.value == 3
        assert Priority.URGENT.value == 4

    def test_ordering(self) -> None:
        assert Priority.LOW > Priority.NORMAL
        assert Priority.URGENT > Priority.HIGH


class TestChangeMetadataDefaults:
    def test_default_priority_is_normal(self) -> None:
        m = ChangeMetadata()
        assert m.priority == Priority.NORMAL

    def test_default_favorite_false(self) -> None:
        m = ChangeMetadata()
        assert m.favorite is False

    def test_default_tags_empty(self) -> None:
        m = ChangeMetadata()
        assert m.tags == ()

    def test_default_blocked_reason_none(self) -> None:
        m = ChangeMetadata()
        assert m.blocked_reason is None

    def test_default_notes_none(self) -> None:
        m = ChangeMetadata()
        assert m.notes is None

    def test_default_order_zero(self) -> None:
        m = ChangeMetadata()
        assert m.order == 0


class TestChangeMetadataCustom:
    def test_set_all_fields(self) -> None:
        m = ChangeMetadata(
            priority=Priority.URGENT,
            tags=("bug", "critical"),
            favorite=True,
            blocked_reason="Needs review",
            notes="Fix ASAP",
            order=5,
        )
        assert m.priority == Priority.URGENT
        assert m.tags == ("bug", "critical")
        assert m.favorite is True
        assert m.blocked_reason == "Needs review"
        assert m.notes == "Fix ASAP"
        assert m.order == 5

    def test_frozen(self) -> None:
        m = ChangeMetadata()
        with pytest.raises(ValueError):
            m.priority = Priority.HIGH

    def test_empty_tags(self) -> None:
        m = ChangeMetadata(tags=())
        assert m.tags == ()


class TestChangeModelBackwardCompat:
    def test_no_metadata_defaults_none(self) -> None:
        c = Change(
            name="test",
            change_dir=Path("/changes/test"),
            absolute_change_dir=Path("/changes/test"),
            artifacts=(),
            is_archived=False,
            state=ChangeState.UNKNOWN,
        )
        assert c.metadata is None

    def test_with_metadata(self) -> None:
        meta = ChangeMetadata(priority=Priority.HIGH, favorite=True)
        c = Change(
            name="test",
            change_dir=Path("/changes/test"),
            absolute_change_dir=Path("/changes/test"),
            artifacts=(),
            is_archived=False,
            state=ChangeState.UNKNOWN,
            metadata=meta,
        )
        assert c.metadata is not None
        assert c.metadata.priority == Priority.HIGH
        assert c.metadata.favorite is True
