from __future__ import annotations

from pathlib import Path

import pytest
from textual.app import App
from textual.widgets import Input

from opsx_tui.domain.open_spec_project import OpenSpecProject
from opsx_tui.domain.project import (
    Diagnostic,
    DiagnosticLevel,
    DiscoverySource,
    Project,
)
from opsx_tui.domain.spec_parser import ParsedSpec, SpecRequirement, SpecScenario
from opsx_tui.domain.status import ChangeStatus
from opsx_tui.domain.workspace import (
    CanonicalSpec,
    Change,
    WorkspaceSnapshot,
)
from opsx_tui.presentation.views.board_view import BoardView
from opsx_tui.presentation.views.changes_view import ChangesView
from opsx_tui.presentation.views.logs_view import LogsView
from opsx_tui.presentation.views.run_view import RunView
from opsx_tui.presentation.views.settings_view import SettingsView
from opsx_tui.presentation.views.specs_view import SpecsView


def _spec(name: str, title: str, reqs: tuple = ()) -> CanonicalSpec:
    parsed = ParsedSpec(
        name=name,
        title=title,
        raw_markdown="",
        requirements=reqs,
        diagnostics=(),
    )
    return CanonicalSpec(
        name=name,
        spec_dir=Path(name),
        spec_file=Path(f"{name}/spec.md"),
        absolute_spec_dir=Path(f"/test/{name}"),
        absolute_spec_file=Path(f"/test/{name}/spec.md"),
        raw_markdown="# Test",
        parsed=parsed,
    )


def _spec_with_diag(name: str, title: str, msg: str) -> CanonicalSpec:
    parsed = ParsedSpec(
        name=name,
        title=title,
        raw_markdown="",
        requirements=(),
        diagnostics=(Diagnostic(level=DiagnosticLevel.WARNING, message=msg),),
    )
    return CanonicalSpec(
        name=name,
        spec_dir=Path(name),
        spec_file=Path(f"{name}/spec.md"),
        absolute_spec_dir=Path(f"/test/{name}"),
        absolute_spec_file=Path(f"/test/{name}/spec.md"),
        raw_markdown="# Empty",
        parsed=parsed,
    )


@pytest.fixture
def project_with_specs() -> OpenSpecProject:
    scenarios = (
        SpecScenario(
            name="Basic case", when_clause="X", then_clause="Y",
            line_start=1, line_end=3,
        ),
    )
    requirements = (
        SpecRequirement(
            name="Must do X",
            body="The system shall do X.",
            scenarios=scenarios,
            line_start=1, line_end=10,
        ),
        SpecRequirement(
            name="Must do Y",
            body="The system shall do Y.",
            scenarios=(),
            line_start=11, line_end=15,
        ),
    )
    specs = (
        _spec("project-foundation", "Project Foundation", requirements),
        _spec("project-discovery", "Project Discovery"),
        _spec_with_diag("broken-spec", "Broken Spec", "File not found"),
    )

    delta_parsed = ParsedSpec(
        name="delta-spec",
        title="Delta Spec",
        raw_markdown="",
        requirements=(),
        diagnostics=(),
    )
    delta_spec = CanonicalSpec(
        name="delta-spec",
        spec_dir=Path("delta-spec"),
        spec_file=Path("delta-spec/spec.md"),
        absolute_spec_dir=Path("/test/delta-spec"),
        absolute_spec_file=Path("/test/delta-spec/spec.md"),
        raw_markdown="# Delta",
        parsed=delta_parsed,
    )
    active_change = Change(
        name="fix-bug",
        change_dir=Path("fix-bug"),
        absolute_change_dir=Path("/test/fix-bug"),
        artifacts=(),
        is_archived=False,
        delta_specs=(delta_spec,),
        state=ChangeStatus.APPLYING,
    )

    snapshot = WorkspaceSnapshot(
        root=Path("/test"),
        openspec_root=Path("/test/openspec"),
        config_yaml=True,
        specs=specs,
        active_changes=(active_change,),
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


# --- 6.1: SpecsView receives opsx_project ---


def test_specs_view_receives_project(project_with_specs: OpenSpecProject) -> None:
    view = SpecsView(project_with_specs)
    assert view.opsx_project is project_with_specs


# --- 6.9: Each view constructor accepts opsx_project ---


def test_board_view_receives_project(project_with_specs: OpenSpecProject) -> None:
    view = BoardView(project_with_specs)
    assert view.opsx_project is project_with_specs


def test_changes_view_receives_project(project_with_specs: OpenSpecProject) -> None:
    view = ChangesView(project_with_specs)
    assert view.opsx_project is project_with_specs


def test_run_view_receives_project(project_with_specs: OpenSpecProject) -> None:
    view = RunView(project_with_specs)
    assert view.opsx_project is project_with_specs


def test_logs_view_receives_project(project_with_specs: OpenSpecProject) -> None:
    view = LogsView(project_with_specs)
    assert view.opsx_project is project_with_specs


def test_settings_view_receives_project(project_with_specs: OpenSpecProject) -> None:
    view = SettingsView(project_with_specs)
    assert view.opsx_project is project_with_specs


# --- 6.2: Tree populated with canonical specs ---


async def test_tree_shows_canonical_specs(project_with_specs: OpenSpecProject) -> None:
    app = App()
    async with app.run_test(size=(80, 24)):
        view = SpecsView(project_with_specs)
        await app.mount(view)
        tree = view.query_one("#spec-tree")
        assert any("Project Foundation" in str(n.label) for n in tree.root.children)
        assert any("Project Discovery" in str(n.label) for n in tree.root.children)


# --- 6.3: Delta specs under "Delta Specs" ---


async def test_tree_shows_delta_specs(project_with_specs: OpenSpecProject) -> None:
    app = App()
    async with app.run_test(size=(80, 24)):
        view = SpecsView(project_with_specs)
        await app.mount(view)
        tree = view.query_one("#spec-tree")
        all_labels = [str(c.label) for c in tree.root.children]
        assert any("Delta" in lb for lb in all_labels)


# --- 6.4: Selecting a spec node updates detail ---


async def test_select_spec_shows_detail(project_with_specs: OpenSpecProject) -> None:
    app = App()
    async with app.run_test(size=(80, 24)) as pilot:
        view = SpecsView(project_with_specs)
        await app.mount(view)
        tree = view.query_one("#spec-tree")
        spec_node = tree.root.children[0]
        tree.select_node(spec_node)
        await pilot.pause()
        await pilot.pause()
        detail_container = view.query_one("#spec-detail")
        detail = detail_container.query_one("#detail-content")
        text = str(detail.renderable)
        assert "Project Foundation" in text


# --- 6.5: Selecting a requirement shows scenarios ---


async def test_select_requirement_shows_scenarios(
    project_with_specs: OpenSpecProject,
) -> None:
    app = App()
    async with app.run_test(size=(80, 24)) as pilot:
        view = SpecsView(project_with_specs)
        await app.mount(view)
        tree = view.query_one("#spec-tree")
        spec_node = tree.root.children[0]
        spec_node.expand()
        req_node = spec_node.children[0]
        tree.select_node(req_node)
        await pilot.pause()
        detail = view.query_one("#detail-content")
        text = str(detail.renderable)
        assert "Basic case" in text


# --- 6.6: Search filters tree ---


async def test_search_filters_tree(project_with_specs: OpenSpecProject) -> None:
    app = App()
    async with app.run_test(size=(80, 24)):
        view = SpecsView(project_with_specs)
        await app.mount(view)
        tree = view.query_one("#spec-tree")
        assert any("Project Foundation" in str(c.label) for c in tree.root.children)
        view.on_input_changed(Input.Changed(input=view, value="Discovery"))
        labels = [str(c.label) for c in tree.root.children]
        assert any("Discovery" in lb for lb in labels)
        assert not any("Foundation" in lb for lb in labels)


# --- 6.7: Empty search restores all ---


async def test_empty_search_restores_all(project_with_specs: OpenSpecProject) -> None:
    app = App()
    async with app.run_test(size=(80, 24)):
        view = SpecsView(project_with_specs)
        await app.mount(view)
        tree = view.query_one("#spec-tree")
        assert len(tree.root.children) >= 3
        view.on_input_changed(Input.Changed(input=view, value="Foundation"))
        assert len(tree.root.children) > 0
        label_texts = [str(c.label) for c in tree.root.children]
        assert any("Foundation" in lb for lb in label_texts)
        view.on_input_changed(Input.Changed(input=view, value=""))
        assert len(tree.root.children) >= 3


# --- 6.8: Diagnostic warning markers ---


async def test_diagnostic_marker_in_tree(project_with_specs: OpenSpecProject) -> None:
    app = App()
    async with app.run_test(size=(80, 24)):
        view = SpecsView(project_with_specs)
        await app.mount(view)
        tree = view.query_one("#spec-tree")
        all_labels = [str(c.label) for c in tree.root.children]
        diag_labels = [lb for lb in all_labels if "\u26a0" in lb]
        assert len(diag_labels) == 1
        assert "Broken" in diag_labels[0]
