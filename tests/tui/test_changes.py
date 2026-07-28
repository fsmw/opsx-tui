from __future__ import annotations

from pathlib import Path

import pytest
from textual.app import App
from textual.widgets import Static

from opsx_tui.domain.change_parser import (
    ChangeState,
    ParsedDesign,
    ParsedDesignDecision,
    ParsedProposal,
    ParsedTaskItem,
    ParsedTaskList,
)
from opsx_tui.domain.open_spec_project import OpenSpecProject
from opsx_tui.domain.project import (
    Diagnostic,
    DiagnosticLevel,
    DiscoverySource,
    Project,
)
from opsx_tui.domain.workspace import (
    Change,
    WorkspaceSnapshot,
)
from opsx_tui.presentation.views.changes_view import ChangesView, _format_change_item


def _make_change(
    name: str,
    is_archived: bool,
    state: ChangeState = ChangeState.ACTIVE,
) -> Change:
    return Change(
        name=name,
        change_dir=Path(name),
        absolute_change_dir=Path(f"/test/{name}"),
        artifacts=(),
        is_archived=is_archived,
        state=state,
    )


def _make_detailed_change(
    name: str,
    is_archived: bool,
    state: ChangeState = ChangeState.ACTIVE,
) -> Change:
    proposal = ParsedProposal(
        sections={"Why": "Need this feature", "What Changes": "Add the feature"},
        known_sections=frozenset({"Why", "What Changes"}),
        unknown_sections=[],
        missing_sections=[],
        line_ranges={"Why": (1, 3), "What Changes": (4, 10)},
        diagnostics=(),
    )
    decisions = (
        ParsedDesignDecision(
            id="D1", title="Use Python", body="Python is great",
            line_start=1, line_end=5,
        ),
    )
    design = ParsedDesign(sections=(), decisions=decisions, diagnostics=())
    tasks = ParsedTaskList(
        items=(
            ParsedTaskItem(
                text="Task 1", checked=True, line_number=1, section="Impl",
            ),
            ParsedTaskItem(
                text="Task 2", checked=False, line_number=2, section="Impl",
            ),
            ParsedTaskItem(
                text="Task 3", checked=True, line_number=3, section="Tests",
            ),
        ),
            total=3,
            completed=2,
            section_map={"Impl": (1, 2), "Tests": (3, 3)},
            diagnostics=(),
        )
    diags = (Diagnostic(level=DiagnosticLevel.WARNING, message="Missing file"),)
    return Change(
        name=name,
        change_dir=Path(name),
        absolute_change_dir=Path(f"/test/{name}"),
        artifacts=(),
        is_archived=is_archived,
        state=state,
        parsed_proposal=proposal,
        parsed_design=design,
        parsed_tasks=tasks,
        artifact_diagnostics=diags,
    )


@pytest.fixture
def project_with_changes() -> OpenSpecProject:
    active = (
        _make_change("fix-bug", is_archived=False),
        _make_detailed_change("add-feature", is_archived=False),
    )
    archived = (
        _make_change("old-change", is_archived=True),
        _make_detailed_change("legacy", is_archived=True, state=ChangeState.ARCHIVED),
    )
    snapshot = WorkspaceSnapshot(
        root=Path("/test"),
        openspec_root=Path("/test/openspec"),
        config_yaml=True,
        specs=(),
        active_changes=active,
        archived_changes=archived,
        diagnostics=(),
        fingerprint="fp-test",
    )
    project = Project(
        root=Path("/test"),
        openspec_root=Path("/test/openspec"),
        discovery_source=DiscoverySource.CLI_ARG,
        is_valid=True,
    )
    return OpenSpecProject(project=project, workspace=snapshot)


def test_changes_view_receives_project(project_with_changes: OpenSpecProject) -> None:
    view = ChangesView(project_with_changes)
    assert view.opsx_project is project_with_changes


def test_format_change_item_shows_state() -> None:
    change = _make_change("test-change", is_archived=False, state=ChangeState.ACTIVE)
    text = _format_change_item(change)
    assert "active" in text
    assert "test-change" in text


def test_format_change_item_shows_progress() -> None:
    change = _make_detailed_change("test-change", is_archived=False)
    text = _format_change_item(change)
    assert "3" in text


def test_format_change_item_shows_priority_indicator() -> None:
    from opsx_tui.domain.metadata import ChangeMetadata, Priority

    change = _make_change("prio-change", is_archived=False)
    meta = ChangeMetadata(priority=Priority.URGENT)
    change2 = change.model_copy(update={"metadata": meta})
    text = _format_change_item(change2)
    assert "[U]" in text


def test_format_change_item_shows_favorite() -> None:
    from opsx_tui.domain.metadata import ChangeMetadata

    change = _make_change("fav-change", is_archived=False)
    meta = ChangeMetadata(favorite=True)
    change2 = change.model_copy(update={"metadata": meta})
    text = _format_change_item(change2)
    assert "\u2605" in text


def test_format_change_item_shows_tags() -> None:
    from opsx_tui.domain.metadata import ChangeMetadata

    change = _make_change("tag-change", is_archived=False)
    meta = ChangeMetadata(tags=("critical",))
    change2 = change.model_copy(update={"metadata": meta})
    text = _format_change_item(change2)
    assert "[critical]" in text


def test_overview_content_shows_name_and_state() -> None:
    from opsx_tui.presentation.views.change_detail_panel import ChangeDetailPanel

    change = _make_change("simple", is_archived=True, state=ChangeState.ARCHIVED)
    text = ChangeDetailPanel._overview_content(change)
    assert "simple" in text
    assert "archived" in text


def test_overview_content_shows_metadata_section() -> None:
    from opsx_tui.domain.metadata import ChangeMetadata, Priority
    from opsx_tui.presentation.views.change_detail_panel import ChangeDetailPanel

    change = _make_change("meta-change", is_archived=False)
    meta = ChangeMetadata(
        priority=Priority.HIGH,
        tags=("ui",),
        favorite=True,
        blocked_reason="Blocked",
        notes="Some notes",
    )
    change2 = change.model_copy(update={"metadata": meta})
    text = ChangeDetailPanel._overview_content(change2)
    assert "HIGH" in text
    assert "\u2605" in text
    assert "ui" in text
    assert "Blocked" in text
    assert "Some notes" in text


def test_overview_content_no_metadata_no_section() -> None:
    from opsx_tui.presentation.views.change_detail_panel import ChangeDetailPanel

    change = _make_change("bare", is_archived=False)
    text = ChangeDetailPanel._overview_content(change)
    assert "Metadata" not in text


def test_tasks_content_shows_progress() -> None:
    from opsx_tui.presentation.views.change_detail_panel import ChangeDetailPanel

    change = _make_detailed_change("full", is_archived=False)
    text = ChangeDetailPanel._tasks_content(change)
    assert "Progress" in text
    assert "2/3" in text


def test_proposal_content_shows_sections() -> None:
    from opsx_tui.presentation.views.change_detail_panel import ChangeDetailPanel

    change = _make_detailed_change("full", is_archived=False)
    text = ChangeDetailPanel._proposal_content(change)
    assert "Need this feature" in text


def test_design_content_shows_decision() -> None:
    from opsx_tui.presentation.views.change_detail_panel import ChangeDetailPanel

    change = _make_detailed_change("full", is_archived=False)
    text = ChangeDetailPanel._design_content(change)
    assert "D1" in text
    assert "Use Python" in text


def test_diagnostics_content_shows_warnings() -> None:
    from opsx_tui.presentation.views.change_detail_panel import ChangeDetailPanel

    change = _make_detailed_change("full", is_archived=False)
    text = ChangeDetailPanel._diagnostics_content(change)
    assert "Diagnostics" in text
    assert "Missing" in text


def test_runs_content_shows_placeholder() -> None:
    from opsx_tui.presentation.views.change_detail_panel import ChangeDetailPanel

    text = ChangeDetailPanel._runs_content(None)
    assert "No runs yet" in text


async def test_list_mounted(project_with_changes: OpenSpecProject) -> None:
    app = App()
    async with app.run_test(size=(80, 24)):
        view = ChangesView(project_with_changes)
        await app.mount(view)
        lv = view.query_one("#change-list")
        assert len(lv.children) >= 3


async def test_search_filters(project_with_changes: OpenSpecProject) -> None:
    from textual.widgets import Input

    app = App()
    async with app.run_test(size=(80, 24)):
        view = ChangesView(project_with_changes)
        await app.mount(view)
        view.on_input_changed(Input.Changed(input=view, value="bug"))
        lv = view.query_one("#change-list")
        assert any(
            "fix-bug" in str(c.query_one(Static).renderable)
            for c in lv.children
        )


async def test_select_change_shows_detail(
    project_with_changes: OpenSpecProject,
) -> None:
    from textual.widgets import ListView

    app = App()
    async with app.run_test(size=(80, 24)):
        view = ChangesView(project_with_changes)
        await app.mount(view)
        lv = view.query_one("#change-list", ListView)
        view.on_list_view_selected(ListView.Selected(lv, lv.children[0]))
        overview = view.query_one("#overview-content")
        text = str(overview.renderable)
        assert "add-feature" in text


async def test_metadata_edit_modal_save_flow() -> None:
    from unittest.mock import MagicMock

    from opsx_tui.domain.metadata import ChangeMetadata
    from opsx_tui.domain.ports import MetadataStore
    from opsx_tui.presentation.modals.metadata_edit_modal import MetadataEditModal

    store = MagicMock(spec=MetadataStore)
    modal = MetadataEditModal(
        store=store,
        change_name="test-change",
        current=ChangeMetadata(priority=2, tags=("a",), notes="hello"),
    )
    assert modal._change_name == "test-change"
    assert modal._metadata.priority == 2
    assert modal._metadata.tags == ("a",)
    assert modal._metadata.notes == "hello"


async def test_metadata_edit_modal_toggles_favorite() -> None:
    from unittest.mock import MagicMock

    from opsx_tui.domain.metadata import ChangeMetadata
    from opsx_tui.domain.ports import MetadataStore
    from opsx_tui.presentation.modals.metadata_edit_modal import MetadataEditModal

    store = MagicMock(spec=MetadataStore)
    modal = MetadataEditModal(
        store=store,
        change_name="test",
        current=ChangeMetadata(),
    )
    assert modal._metadata.favorite is False
    modal.action_toggle_favorite()
    assert modal._metadata.favorite is True
    modal.action_toggle_favorite()
    assert modal._metadata.favorite is False


async def test_metadata_edit_modal_set_priority() -> None:
    from unittest.mock import MagicMock

    from opsx_tui.domain.metadata import Priority
    from opsx_tui.domain.ports import MetadataStore
    from opsx_tui.presentation.modals.metadata_edit_modal import MetadataEditModal

    store = MagicMock(spec=MetadataStore)
    modal = MetadataEditModal(
        store=store,
        change_name="test",
        current=None,
    )
    assert modal._metadata.priority == Priority.NORMAL
    modal.action_set_priority_3()
    assert modal._metadata.priority == Priority.HIGH


async def test_detail_parsed_content(project_with_changes: OpenSpecProject) -> None:
    from textual.widgets import ListView

    app = App()
    async with app.run_test(size=(80, 24)):
        view = ChangesView(project_with_changes)
        await app.mount(view)
        lv = view.query_one("#change-list", ListView)
        for child in lv.children:
            child_text = str(child.query_one(Static).renderable)
            if "add-feature" in child_text:
                view.on_list_view_selected(ListView.Selected(lv, child))
                break
        overview = view.query_one("#overview-content")
        overview_text = str(overview.renderable)
        assert "active" in overview_text
        assert "add-feature" in overview_text
        proposal = view.query_one("#proposal-content")
        proposal_text = str(proposal.renderable)
        assert "Need this feature" in proposal_text
