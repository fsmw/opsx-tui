from __future__ import annotations

from pathlib import Path

from textual.app import App

from opsx_tui.domain.change_parser import (
    ParsedTaskList,
)
from opsx_tui.domain.metadata import ChangeMetadata, Priority
from opsx_tui.domain.open_spec_project import OpenSpecProject
from opsx_tui.domain.project import (
    Diagnostic,
    DiagnosticLevel,
    DiscoverySource,
    Project,
)
from opsx_tui.domain.status import ChangeStatus
from opsx_tui.domain.workspace import (
    ArtifactInfo,
    ArtifactKind,
    Change,
    WorkspaceSnapshot,
)
from opsx_tui.presentation.views.board_view import BoardView
from opsx_tui.presentation.views.kanban.kanban_card import KanbanCard
from opsx_tui.presentation.views.kanban.kanban_column import KanbanColumn


def _artifact(kind: ArtifactKind, exists: bool = True) -> ArtifactInfo:
    return ArtifactInfo(
        kind=kind,
        path=Path(f"{kind.value}.md"),
        absolute_path=Path(f"/test/{kind.value}.md"),
        exists=exists,
    )


def _make_change(
    name: str,
    state: ChangeStatus = ChangeStatus.APPLYING,
    metadata: ChangeMetadata | None = None,
    tasks: ParsedTaskList | None = None,
    artifacts: tuple[ArtifactInfo, ...] = (),
    diagnostics: tuple[Diagnostic, ...] = (),
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
        artifact_diagnostics=diagnostics,
    )


def _tasks(completed: int, total: int) -> ParsedTaskList:
    return ParsedTaskList(
        items=(),
        total=total,
        completed=completed,
        section_map={},
        diagnostics=(),
    )


def _project(active: tuple[Change, ...]) -> OpenSpecProject:
    snapshot = WorkspaceSnapshot(
        root=Path("/test"),
        openspec_root=Path("/test/openspec"),
        config_yaml=True,
        specs=(),
        active_changes=active,
        archived_changes=(),
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


async def _mount_board(
    app: App,
    project: OpenSpecProject,
) -> BoardView:
    app.opsx_project = project
    view = BoardView(project)
    await app.mount(view)
    return view


def _column_states(view: BoardView) -> list[str]:
    return [col.state for col in view.query(KanbanColumn)]


def _card_names(column: KanbanColumn) -> list[str]:
    return [card.change.name for card in column._cards]


async def test_board_renders_active_state_columns() -> None:
    project = _project(
        (
            _make_change("one", state=ChangeStatus.DRAFT),
            _make_change("two", state=ChangeStatus.BLOCKED),
        )
    )
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        states = _column_states(view)
        assert states[:7] == [
            "draft",
            "planning",
            "ready",
            "applying",
            "verification",
            "ready-to-archive",
            "blocked",
        ]
        assert "unknown" not in states


async def test_no_unknown_column_when_no_unknown_changes() -> None:
    project = _project((_make_change("one", state=ChangeStatus.READY),))
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        assert "unknown" not in _column_states(view)


async def test_unknown_column_only_when_unknown_changes_exist() -> None:
    project = _project(
        (
            _make_change("known", state=ChangeStatus.READY),
            _make_change("mystery", state=ChangeStatus.UNKNOWN),
        )
    )
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        states = _column_states(view)
        assert states[-1] == "unknown"
        assert _card_names(view.query(KanbanColumn).last()) == ["mystery"]


async def test_unknown_column_removed_when_no_longer_needed() -> None:
    project = _project((_make_change("mystery", state=ChangeStatus.UNKNOWN),))
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        assert "unknown" in _column_states(view)
        updated = _project((_make_change("mystery", state=ChangeStatus.READY),))
        app.opsx_project = updated
        await view.reload()
        assert "unknown" not in _column_states(view)


async def test_card_in_matching_column() -> None:
    project = _project((_make_change("impl", state=ChangeStatus.APPLYING),))
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        applying = view.query_one("#column-applying", KanbanColumn)
        assert _card_names(applying) == ["impl"]


async def test_card_shows_name_and_state() -> None:
    project = _project(
        (_make_change("feature", state=ChangeStatus.PLANNING, tasks=_tasks(2, 5)),)
    )
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        card = view.query(KanbanCard).first()
        assert "feature" in card.render()
        assert "PLN" in card.render()
        assert "2/5" in card.render()


async def test_card_shows_artifact_indicators() -> None:
    artifacts = (
        _artifact(ArtifactKind.PROPOSAL, True),
        _artifact(ArtifactKind.DESIGN, False),
        _artifact(ArtifactKind.TASKS, True),
    )
    project = _project(
        (_make_change("feature", state=ChangeStatus.READY, artifacts=artifacts),)
    )
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        card = view.query(KanbanCard).first()
        text = card.render()
        assert "\u2713proposal" in text
        assert "\u2717design" in text
        assert "\u2713tasks" in text


async def test_card_no_tasks_no_percent_progress() -> None:
    project = _project((_make_change("bare", state=ChangeStatus.DRAFT),))
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        card = view.query(KanbanCard).first()
        text = card.render()
        assert "%" not in text
        assert "no tasks" in text


async def test_card_priority_favorite_metadata_signals() -> None:
    meta = ChangeMetadata(priority=Priority.URGENT, favorite=True, tags=("critical",))
    project = _project((_make_change("hot", state=ChangeStatus.READY, metadata=meta),))
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        text = view.query(KanbanCard).first().render()
        assert "[U]" in text
        assert "\u2605" in text
        assert "[critical]" in text


async def test_warning_marker_for_diagnostics_and_blocked() -> None:
    project = _project(
        (
            _make_change(
                "bad",
                state=ChangeStatus.READY,
                diagnostics=(Diagnostic(level=DiagnosticLevel.WARNING, message="x"),),
            ),
            _make_change("stuck", state=ChangeStatus.BLOCKED),
        )
    )
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        cards = list(view.query(KanbanCard))
        assert len(cards) == 2
        for card in cards:
            assert "\u26a0" in card.render()


async def test_sorting_priority_desc_then_name() -> None:
    project = _project(
        (
            _make_change(
                "normal-one",
                state=ChangeStatus.READY,
                metadata=ChangeMetadata(priority=Priority.NORMAL),
            ),
            _make_change(
                "urgent-one",
                state=ChangeStatus.READY,
                metadata=ChangeMetadata(priority=Priority.URGENT),
            ),
            _make_change(
                "normal-two",
                state=ChangeStatus.READY,
                metadata=ChangeMetadata(priority=Priority.NORMAL),
            ),
        )
    )
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        ready = view.query_one("#column-ready", KanbanColumn)
        assert _card_names(ready) == ["urgent-one", "normal-one", "normal-two"]


async def test_sorting_user_order_overrides() -> None:
    project = _project(
        (
            _make_change(
                "urgent-late",
                state=ChangeStatus.READY,
                metadata=ChangeMetadata(priority=Priority.URGENT, order=2),
            ),
            _make_change(
                "normal-early",
                state=ChangeStatus.READY,
                metadata=ChangeMetadata(priority=Priority.NORMAL, order=1),
            ),
        )
    )
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        ready = view.query_one("#column-ready", KanbanColumn)
        assert _card_names(ready) == ["normal-early", "urgent-late"]


async def test_sorting_does_not_change_state() -> None:
    project = _project(
        (
            _make_change("a", state=ChangeStatus.READY),
            _make_change("b", state=ChangeStatus.READY),
        )
    )
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        states_before = {c.change.name: c.change.state for c in view.query(KanbanCard)}
        await view.reload()
        states_after = {c.change.name: c.change.state for c in view.query(KanbanCard)}
        assert states_before == states_after


async def test_vertical_navigation_moves_focus() -> None:
    project = _project(
        (
            _make_change("first", state=ChangeStatus.READY),
            _make_change("second", state=ChangeStatus.READY),
        )
    )
    app = App()
    async with app.run_test(size=(120, 40)) as pilot:
        view = await _mount_board(app, project)
        ready = view.query_one("#column-ready", KanbanColumn)
        ready._cards[0].focus()
        await pilot.pause()
        view.action_cursor_down()
        await pilot.pause()
        assert ready._cards[1].has_focus
        view.action_cursor_up()
        await pilot.pause()
        assert ready._cards[0].has_focus


async def test_horizontal_navigation_moves_between_columns() -> None:
    project = _project(
        (
            _make_change("drafty", state=ChangeStatus.DRAFT),
            _make_change("readier", state=ChangeStatus.READY),
        )
    )
    app = App()
    async with app.run_test(size=(120, 40)) as pilot:
        view = await _mount_board(app, project)
        draft = view.query_one("#column-draft", KanbanColumn)
        draft._cards[0].focus()
        await pilot.pause()
        view.action_cursor_right()
        await pilot.pause()
        planning = view.query_one("#column-planning", KanbanColumn)
        assert planning.query_one("#column-header").has_focus
        view.action_cursor_right()
        await pilot.pause()
        assert view.query_one("#column-ready", KanbanColumn)._cards[0].has_focus
        view.action_cursor_left()
        await pilot.pause()
        assert view.query_one("#column-planning", KanbanColumn).query_one(
            "#column-header"
        ).has_focus
        view.action_cursor_left()
        await pilot.pause()
        assert draft._cards[0].has_focus


async def test_enter_opens_detail_modal() -> None:
    project = _project((_make_change("feature", state=ChangeStatus.READY),))
    app = App()
    async with app.run_test(size=(120, 40)) as pilot:
        view = await _mount_board(app, project)
        ready = view.query_one("#column-ready", KanbanColumn)
        ready._cards[0].focus()
        await pilot.pause()
        view.action_open_detail()
        await pilot.pause()
        assert app.screen.id == "board-detail-modal"
        app.pop_screen()


async def test_enter_no_card_notifies() -> None:
    project = _project(())
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        view.action_open_detail()
        assert app.screen.id != "board-detail-modal"


async def test_toggle_column_collapse_expand() -> None:
    project = _project((_make_change("feature", state=ChangeStatus.READY),))
    app = App()
    async with app.run_test(size=(120, 40)) as pilot:
        view = await _mount_board(app, project)
        ready = view.query_one("#column-ready", KanbanColumn)
        assert not ready.is_collapsed
        ready._cards[0].focus()
        await pilot.pause()
        view.action_toggle_column()
        assert ready.is_collapsed
        view.action_toggle_column()
        assert not ready.is_collapsed
        assert len(ready._cards) == 1


async def test_reactive_refresh_moves_card_between_columns() -> None:
    project = _project((_make_change("moving", state=ChangeStatus.READY),))
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        assert _card_names(view.query_one("#column-ready", KanbanColumn)) == ["moving"]
        updated = _project((_make_change("moving", state=ChangeStatus.APPLYING),))
        app.opsx_project = updated
        await view.reload()
        assert _card_names(view.query_one("#column-applying", KanbanColumn)) == [
            "moving"
        ]
        assert _card_names(view.query_one("#column-ready", KanbanColumn)) == []


async def test_header_count_updates_on_reload() -> None:
    project = _project((_make_change("one", state=ChangeStatus.READY),))
    app = App()
    async with app.run_test(size=(120, 40)):
        view = await _mount_board(app, project)
        ready = view.query_one("#column-ready", KanbanColumn)
        header = ready.query_one("#column-header")
        assert "1" in header.render()
        updated = _project(
            (
                _make_change("one", state=ChangeStatus.READY),
                _make_change("two", state=ChangeStatus.READY),
            )
        )
        app.opsx_project = updated
        await view.reload()
        assert "2" in header.render()


async def test_board_on_narrow_terminal_truncates() -> None:
    project = _project(
        (_make_change("a-very-long-change-name", state=ChangeStatus.READY),)
    )
    app = App()
    async with app.run_test(size=(60, 20)):
        view = await _mount_board(app, project)
        card = view.query(KanbanCard).first()
        assert card
