from __future__ import annotations

from collections.abc import Iterable

from textual.app import ComposeResult
from textual.widgets import Static, TabbedContent, TabPane
from textual.widget import Widget

from opsx_tui.domain.metadata import ChangeMetadata
from opsx_tui.domain.workspace import ArtifactKind, Change


def _progress_bar(completed: int, total: int, width: int = 20) -> str:
    if total == 0:
        return "|----------| 0/0"
    filled = int(width * completed / total)
    bar = "=" * (filled - 1 if filled > 0 else 0) + (">" if 0 < filled < width else "")
    bar += "-" * (width - len(bar))
    pct = int(100 * completed / total)
    return f"|{bar}| {completed}/{total} ({pct}%)"


class ChangeDetailPanel(Widget):
    def compose(self) -> Iterable[Widget]:
        with TabbedContent(initial="overview"):
            with TabPane("Overview", id="overview"):
                yield Static("", id="overview-content")
            with TabPane("Proposal", id="proposal"):
                yield Static("", id="proposal-content")
            with TabPane("Design", id="design"):
                yield Static("", id="design-content")
            with TabPane("Specs", id="specs"):
                yield Static("", id="specs-content")
            with TabPane("Tasks", id="tasks"):
                yield Static("", id="tasks-content")
            with TabPane("Runs", id="runs"):
                yield Static("", id="runs-content")
            with TabPane("Diagnostics", id="diagnostics"):
                yield Static("", id="diagnostics-content")

    def show_change(self, change: Change) -> None:
        self.query_one("#overview-content", Static).update(
            self._overview_content(change)
        )
        self.query_one("#proposal-content", Static).update(
            self._proposal_content(change)
        )
        self.query_one("#design-content", Static).update(
            self._design_content(change)
        )
        self.query_one("#specs-content", Static).update(
            self._specs_content(change)
        )
        self.query_one("#tasks-content", Static).update(
            self._tasks_content(change)
        )
        self.query_one("#runs-content", Static).update(
            self._runs_content(change)
        )
        self.query_one("#diagnostics-content", Static).update(
            self._diagnostics_content(change)
        )

    @staticmethod
    def _overview_content(change: Change) -> str:
        lines = [f"# {change.name}", f"**State:** {change.state.value}", ""]
        present: list[str] = []
        missing: list[str] = []
        for a in change.artifacts:
            if a.exists:
                present.append(a.kind.value)
            else:
                missing.append(a.kind.value)
        if present:
            lines.append(f"**Artifacts present:** {', '.join(present)}")
        if missing:
            lines.append(f"**Artifacts missing:** {', '.join(missing)}")
        if change.parsed_tasks is not None:
            bar = _progress_bar(
                change.parsed_tasks.completed, change.parsed_tasks.total
            )
            lines.append(f"**Progress:** {bar}")
        if change.metadata:
            m: ChangeMetadata = change.metadata
            lines.append("")
            lines.append("## Metadata")
            pri_name = m.priority.name
            lines.append(f"**Priority:** {pri_name}")
            if m.favorite:
                lines.append("**Favorite:** \u2605")
            if m.tags:
                lines.append(f"**Tags:** {', '.join(m.tags)}")
            if m.blocked_reason:
                lines.append(f"**Blocked:** {m.blocked_reason}")
            if m.notes:
                lines.append(f"**Notes:** {m.notes}")
        return "\n".join(lines)

    @staticmethod
    def _proposal_content(change: Change) -> str:
        if change.parsed_proposal is None:
            return "No proposal available"
        sections = change.parsed_proposal.sections
        lines: list[str] = []
        for key, val in sections.items():
            lines.append(f"## {key}")
            lines.append(val.strip())
            lines.append("")
        if not lines:
            return "No proposal sections found"
        return "\n".join(lines)

    @staticmethod
    def _design_content(change: Change) -> str:
        if change.parsed_design is None:
            return "No design available"
        decisions = change.parsed_design.decisions
        if not decisions:
            return "No design decisions recorded"
        lines: list[str] = []
        for d in decisions:
            lines.append(f"### {d.id}: {d.title}")
            lines.append(d.body.strip())
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _specs_content(change: Change) -> str:
        if not change.delta_specs:
            return "No delta specs"
        lines: list[str] = []
        for ds in change.delta_specs:
            label = ds.parsed.title if ds.parsed else ds.name
            lines.append(f"- {label}")
        return "\n".join(lines)

    @staticmethod
    def _tasks_content(change: Change) -> str:
        if change.parsed_tasks is None:
            return "No tasks available"
        pt = change.parsed_tasks
        lines: list[str] = []
        bar = _progress_bar(pt.completed, pt.total)
        lines.append(f"Progress: {bar}")
        lines.append("")
        current_section: str | None = None
        for item in pt.items:
            if item.section and item.section != current_section:
                lines.append(f"**{item.section}**")
                current_section = item.section
            check = "[x]" if item.checked else "[ ]"
            lines.append(f"- {check} {item.text}")
        return "\n".join(lines)

    @staticmethod
    def _runs_content(change: Change) -> str:
        return "No runs yet. Runs will appear here after agent execution."

    @staticmethod
    def _diagnostics_content(change: Change) -> str:
        lines: list[str] = []
        if change.artifact_diagnostics:
            lines.append("## Diagnostics")
            for diag in change.artifact_diagnostics:
                level = diag.level.value if hasattr(diag.level, "value") else diag.level
                lines.append(f"- [{level}] {diag.message}")
        known_names = {ArtifactKind.PROPOSAL, ArtifactKind.DESIGN, ArtifactKind.TASKS, ArtifactKind.SPECS}
        unknown = [a.path.name for a in change.artifacts if a.kind not in known_names and a.exists]
        if unknown:
            lines.append("")
            lines.append("## Unknown files")
            for name in unknown:
                lines.append(f"- `{name}`")
        if not lines:
            return "No diagnostics"
        return "\n".join(lines)
