from __future__ import annotations

import re
from collections.abc import Sequence
from enum import StrEnum

from pydantic import BaseModel

from opsx_tui.domain.project import Diagnostic, DiagnosticLevel


class ChangeState(StrEnum):
    UNKNOWN = "unknown"
    INCOMPLETE = "incomplete"
    PARTIALLY_VALID = "partially_valid"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ParsedProposal(BaseModel, frozen=True):
    sections: dict[str, str]
    known_sections: frozenset
    unknown_sections: list[str]
    missing_sections: list[str]
    line_ranges: dict[str, tuple[int, int]]
    diagnostics: tuple[Diagnostic, ...]


class ParsedDesignSection(BaseModel, frozen=True):
    name: str
    body: str
    line_start: int
    line_end: int


class ParsedDesignDecision(BaseModel, frozen=True):
    id: str
    title: str
    body: str
    line_start: int
    line_end: int


class ParsedDesign(BaseModel, frozen=True):
    sections: tuple[ParsedDesignSection, ...]
    decisions: tuple[ParsedDesignDecision, ...]
    diagnostics: tuple[Diagnostic, ...]


class ParsedTaskItem(BaseModel, frozen=True):
    text: str
    checked: bool
    line_number: int
    section: str


class ParsedTaskList(BaseModel, frozen=True):
    items: tuple[ParsedTaskItem, ...]
    total: int
    completed: int
    section_map: dict[str, tuple[int, int]]
    diagnostics: tuple[Diagnostic, ...]


_KNOWN_PROPOSAL_SECTIONS: frozenset = frozenset({
    "Why", "What Changes", "Capabilities", "Impact",
})
_PROPOSAL_SECTION_RE = re.compile(r"^## (.+)$")
_DESIGN_DECISION_RE = re.compile(r"^### (D\d+):\s*(.*)$")
_DESIGN_SECTION_RE = re.compile(r"^## (.+)$")
_TASK_CHECKBOX_RE = re.compile(r"^(\s*)- \[([ xX])\] (.+)$")
_TASK_SECTION_RE = re.compile(r"^## (.+)$")
_FENCED_CODE_RE = re.compile(r"^```")


def parse_proposal_markdown(markdown: str) -> ParsedProposal:
    lines = markdown.split("\n")
    diagnostics: list[Diagnostic] = []
    sections: dict[str, str] = {}
    line_ranges: dict[str, tuple[int, int]] = {}

    if not markdown.strip():
        diagnostics.append(Diagnostic(
            level=DiagnosticLevel.INFO,
            message="Proposal markdown is empty",
        ))
        return ParsedProposal(
            sections={},
            known_sections=_KNOWN_PROPOSAL_SECTIONS,
            unknown_sections=[],
            missing_sections=list(_KNOWN_PROPOSAL_SECTIONS),
            line_ranges={},
            diagnostics=tuple(diagnostics),
        )

    current_section: str | None = None
    section_start: int = 0
    section_lines: list[str] = []

    for line_no, line in enumerate(lines, 1):
        stripped = line.rstrip()
        section_match = _PROPOSAL_SECTION_RE.match(stripped)
        if section_match:
            if current_section is not None:
                sections[current_section] = "\n".join(section_lines).strip()
                line_ranges[current_section] = (section_start, line_no - 1)
            current_section = section_match.group(1).strip()
            section_start = line_no
            section_lines = []
        else:
            if current_section is not None:
                section_lines.append(line)

    if current_section is not None:
        sections[current_section] = "\n".join(section_lines).strip()
        line_ranges[current_section] = (section_start, len(lines))

    found_sections = frozenset(sections.keys())
    unknown_sections = list(found_sections - _KNOWN_PROPOSAL_SECTIONS)
    missing_sections = list(_KNOWN_PROPOSAL_SECTIONS - found_sections)

    for us in unknown_sections:
        diagnostics.append(Diagnostic(
            level=DiagnosticLevel.WARNING,
            message=f"Unknown proposal section: {us}",
        ))
    for ms in missing_sections:
        diagnostics.append(Diagnostic(
            level=DiagnosticLevel.WARNING,
            message=f"Missing proposal section: {ms}",
        ))

    return ParsedProposal(
        sections=sections,
        known_sections=_KNOWN_PROPOSAL_SECTIONS,
        unknown_sections=sorted(unknown_sections),
        missing_sections=sorted(missing_sections),
        line_ranges=line_ranges,
        diagnostics=tuple(diagnostics),
    )


def parse_design_markdown(markdown: str) -> ParsedDesign:
    lines = markdown.split("\n")
    diagnostics: list[Diagnostic] = []
    sections: list[ParsedDesignSection] = []
    decisions: list[ParsedDesignDecision] = []

    if not markdown.strip():
        diagnostics.append(Diagnostic(
            level=DiagnosticLevel.INFO,
            message="Design markdown is empty",
        ))
        return ParsedDesign(
            sections=(),
            decisions=(),
            diagnostics=tuple(diagnostics),
        )

    current_section: str | None = None
    section_start: int = 0
    section_lines: list[str] = []

    inside_decisions = False
    decision_id: str = ""
    decision_title: str = ""
    decision_start: int = 0
    decision_lines: list[str] = []

    def finalize_section(end_line: int) -> None:
        nonlocal current_section, section_start, section_lines
        if current_section is not None:
            sections.append(ParsedDesignSection(
                name=current_section,
                body="\n".join(section_lines).strip(),
                line_start=section_start,
                line_end=end_line,
            ))
            current_section = None
            section_lines = []

    def finalize_decision(end_line: int) -> None:
        nonlocal decision_id, decision_title, decision_start, decision_lines
        if decision_id or decision_lines:
            decisions.append(ParsedDesignDecision(
                id=decision_id,
                title=decision_title,
                body="\n".join(decision_lines).strip(),
                line_start=decision_start,
                line_end=end_line,
            ))
            decision_id = ""
            decision_title = ""
            decision_lines = []

    for line_no, line in enumerate(lines, 1):
        stripped = line.rstrip()

        sec_match = _DESIGN_SECTION_RE.match(stripped)
        if sec_match:
            finalize_decision(line_no - 1)
            finalize_section(line_no - 1)
            section_name = sec_match.group(1).strip()
            current_section = section_name
            section_start = line_no
            inside_decisions = section_name == "Decisions"
            continue

        if inside_decisions:
            dec_match = _DESIGN_DECISION_RE.match(stripped)
            if dec_match:
                finalize_decision(line_no - 1)
                decision_id = dec_match.group(1)
                decision_title = dec_match.group(2).strip()
                decision_start = line_no
                continue

            if stripped.startswith("### ") and not stripped.startswith("### D"):
                finalize_decision(line_no - 1)
                diagnostics.append(Diagnostic(
                    level=DiagnosticLevel.WARNING,
                    message=f"Decision at line {line_no} does not match D\\d+: pattern",
                ))
                decision_id = ""
                title_text = stripped[4:].strip()
                decision_title = title_text
                decision_start = line_no
                continue

            if decision_start > 0:
                decision_lines.append(line)
                continue

        if current_section is not None:
            section_lines.append(line)

    finalize_decision(len(lines))
    finalize_section(len(lines))

    if not decisions:
        diagnostics.append(Diagnostic(
            level=DiagnosticLevel.INFO,
            message="No decisions found in design markdown",
        ))

    return ParsedDesign(
        sections=tuple(sections),
        decisions=tuple(decisions),
        diagnostics=tuple(diagnostics),
    )


def parse_task_markdown(markdown: str) -> ParsedTaskList:
    lines = markdown.split("\n")
    diagnostics: list[Diagnostic] = []
    items: list[ParsedTaskItem] = []
    section_map: dict[str, tuple[int, int]] = {}

    if not markdown.strip():
        return ParsedTaskList(
            items=(),
            total=0,
            completed=0,
            section_map={},
            diagnostics=(),
        )

    current_section: str = ""
    inside_code_block = False
    first_item_in_section: int | None = None

    for line_no, line in enumerate(lines, 1):
        stripped = line.rstrip()

        if _FENCED_CODE_RE.match(stripped):
            inside_code_block = not inside_code_block
            continue

        if inside_code_block:
            continue

        sec_match = _TASK_SECTION_RE.match(stripped)
        if sec_match:
            if current_section and first_item_in_section is not None:
                section_map[current_section] = (first_item_in_section, line_no - 1)
            current_section = sec_match.group(1).strip()
            first_item_in_section = None
            continue

        checkbox_match = _TASK_CHECKBOX_RE.match(stripped)
        if checkbox_match:
            indent = checkbox_match.group(1)
            checkbox_char = checkbox_match.group(2)
            text = indent + checkbox_char + " " + checkbox_match.group(3)
            checked = checkbox_char in ("x", "X")
            section = current_section if current_section else ""
            if first_item_in_section is None:
                first_item_in_section = line_no
            items.append(ParsedTaskItem(
                text=text,
                checked=checked,
                line_number=line_no,
                section=section,
            ))

    if current_section and first_item_in_section is not None:
        section_map[current_section] = (first_item_in_section, len(lines))

    total = len(items)
    completed = sum(1 for i in items if i.checked)

    return ParsedTaskList(
        items=tuple(items),
        total=total,
        completed=completed,
        section_map=section_map,
        diagnostics=tuple(diagnostics),
    )


def infer_change_state(
    is_archived: bool,
    has_artifacts: dict[str, bool],
    artifact_diagnostics: Sequence[Diagnostic],
) -> ChangeState:
    if is_archived:
        return ChangeState.ARCHIVED
    if not any(has_artifacts.values()):
        return ChangeState.UNKNOWN
    if not all(has_artifacts.get(k, False) for k in ("proposal", "design", "tasks")):
        return ChangeState.INCOMPLETE
    severe = (DiagnosticLevel.WARNING, DiagnosticLevel.ERROR)
    content_diagnostics = [d for d in artifact_diagnostics if d.level in severe]
    if content_diagnostics:
        return ChangeState.PARTIALLY_VALID
    return ChangeState.ACTIVE
