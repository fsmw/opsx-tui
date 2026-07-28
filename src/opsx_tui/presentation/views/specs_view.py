from __future__ import annotations

from collections.abc import Iterable

from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer
from textual.widgets import Input, Static, Tree
from textual.widgets.tree import TreeNode
from textual.widget import Widget

from opsx_tui.domain.open_spec_project import OpenSpecProject
from opsx_tui.domain.spec_parser import name_to_title
from opsx_tui.domain.workspace import CanonicalSpec


class SpecDetailContent:
    @staticmethod
    def for_spec(spec: CanonicalSpec) -> str:
        lines = [f"# {spec.parsed.title if spec.parsed else name_to_title(spec.name)}"]
        if spec.absolute_spec_file:
            lines.append(f"**File:** `{spec.absolute_spec_file}`")
        if spec.raw_markdown is not None:
            lines.append(f"**Size:** {len(spec.raw_markdown)} chars")
        lines.append("")
        if spec.parsed and spec.parsed.diagnostics:
            lines.append("## Diagnostics")
            for d in spec.parsed.diagnostics:
                lines.append(f"- {d.message}")
            lines.append("")
        if spec.parsed and spec.parsed.requirements:
            lines.append("## Requirements")
            for r in spec.parsed.requirements:
                lines.append(f"- **{r.name}**")
                body = r.body.strip()
                if body:
                    lines.append(f"  {body}")
        return "\n".join(lines)

    @staticmethod
    def for_requirement(req) -> str:
        lines = [f"# {req.name}", "", req.body.strip()]
        if req.scenarios:
            lines.append("")
            lines.append("## Scenarios")
            for s in req.scenarios:
                lines.append(f"### {s.name}")
                if s.when_clause:
                    lines.append(f"- **WHEN** {s.when_clause}")
                if s.then_clause:
                    lines.append(f"- **THEN** {s.then_clause}")
        return "\n".join(lines)

    @staticmethod
    def for_scenario(scenario) -> str:
        lines = [f"# {scenario.name}", ""]
        if scenario.when_clause:
            lines.append(f"- **WHEN** {scenario.when_clause}")
        if scenario.then_clause:
            lines.append(f"- **THEN** {scenario.then_clause}")
        return "\n".join(lines)


class SpecsView(Widget):
    def __init__(self, opsx_project: OpenSpecProject, id: str | None = None) -> None:
        super().__init__(id=id)
        self.opsx_project: OpenSpecProject = opsx_project

    def compose(self) -> Iterable[Widget]:
        yield Input(placeholder="Search specs...", id="spec-search")
        with Horizontal(id="spec-browser-panel"):
            yield Tree("Specs", id="spec-tree")
            with ScrollableContainer(id="spec-detail"):
                yield Static("Select a spec from the tree", id="detail-content")

    def _add_scenario_nodes(self, req_node: TreeNode, req) -> None:
        for sc in req.scenarios:
            req_node.add_leaf(sc.name, data={
                "type": "scenario",
                "scenario": sc,
            })

    def _add_requirement_nodes(self, spec_node: TreeNode, reqs) -> None:
        for req in reqs:
            req_node = spec_node.add(req.name, data={
                "type": "requirement",
                "requirement": req,
            })
            if req.scenarios:
                self._add_scenario_nodes(req_node, req)

    def _build_tree_from_filter(self, tree: Tree, filter_text: str) -> None:
        tree.clear()
        root = tree.root
        query = filter_text.strip().lower()

        for spec in self.opsx_project.workspace.specs:
            label = spec.parsed.title if spec.parsed else name_to_title(spec.name)
            if spec.parsed and spec.parsed.diagnostics:
                label += " \u26a0"
            if query:
                spec_matches = query in label.lower()
                if spec.parsed and spec.parsed.requirements:
                    matching_reqs = [
                        r for r in spec.parsed.requirements
                        if query in r.name.lower()
                    ]
                    if spec_matches or matching_reqs:
                        spec_node = root.add(label, data={
                            "type": "spec", "spec": spec,
                        })
                        if matching_reqs:
                            self._add_requirement_nodes(spec_node, matching_reqs)
                elif spec_matches:
                    root.add_leaf(label, data={"type": "spec", "spec": spec})
            else:
                spec_node = root.add(label, data={
                    "type": "spec", "spec": spec,
                })
                spec_node.allow_expand = True
                if spec.parsed and spec.parsed.requirements:
                    self._add_requirement_nodes(spec_node, spec.parsed.requirements)

        if not query:
            deltas_root = root.add("Delta Specs", data={"type": "delta-root"})
            deltas_root.allow_expand = True
            for change in self.opsx_project.workspace.active_changes:
                if change.delta_specs:
                    change_node = deltas_root.add(
                        change.name,
                        data={"type": "delta-change", "change": change},
                    )
                    change_node.allow_expand = True
                    for ds in change.delta_specs:
                        ds_label = ds.parsed.title if ds.parsed else name_to_title(ds.name)
                        ds_node = change_node.add(
                            ds_label + " (delta)",
                            data={"type": "delta-spec", "spec": ds},
                        )
                        ds_node.allow_expand = True
                        if ds.parsed and ds.parsed.requirements:
                            self._add_requirement_nodes(ds_node, ds.parsed.requirements)

        root.expand()

    def on_mount(self) -> None:
        tree = self.query_one("#spec-tree", Tree)
        self._build_tree_from_filter(tree, "")

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        data = event.node.data
        if data is None:
            return
        node_type = data.get("type")
        if node_type == "spec" or node_type == "delta-spec":
            spec: CanonicalSpec = data["spec"]
            text = SpecDetailContent.for_spec(spec)
        elif node_type == "requirement":
            req = data["requirement"]
            text = SpecDetailContent.for_requirement(req)
        elif node_type == "scenario":
            scenario = data["scenario"]
            text = SpecDetailContent.for_scenario(scenario)
        else:
            text = "Select a spec, requirement, or scenario from the tree"
        self.query_one("#detail-content", Static).update(text)

    def on_input_changed(self, event: Input.Changed) -> None:
        tree = self.query_one("#spec-tree", Tree)
        self._build_tree_from_filter(tree, event.value)
