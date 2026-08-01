from __future__ import annotations

import pytest
from pydantic import ValidationError

from opsx_tui.domain.change_parser import (
    ParsedDesign,
    ParsedDesignDecision,
    ParsedDesignSection,
    ParsedProposal,
    ParsedTaskItem,
    ParsedTaskList,
    parse_design_markdown,
    parse_proposal_markdown,
    parse_task_markdown,
)


class TestParsedProposalModel:
    def test_frozen(self) -> None:
        p = ParsedProposal(
            sections={}, known_sections=frozenset(),
            unknown_sections=[], missing_sections=[],
            line_ranges={}, diagnostics=(),
        )
        with pytest.raises(ValidationError):
            p.sections = {"x": "y"}

    def test_defaults(self) -> None:
        p = ParsedProposal(
            sections={}, known_sections=frozenset(),
            unknown_sections=[], missing_sections=[],
            line_ranges={}, diagnostics=(),
        )
        assert p.sections == {}
        assert p.diagnostics == ()


class TestParsedDesignModel:
    def test_frozen_section(self) -> None:
        s = ParsedDesignSection(name="Ctx", body="text", line_start=1, line_end=5)
        with pytest.raises(ValidationError):
            s.name = "changed"

    def test_frozen_decision(self) -> None:
        d = ParsedDesignDecision(id="D1", title="X", body="y", line_start=1, line_end=2)
        with pytest.raises(ValidationError):
            d.id = "D2"

    def test_frozen_design(self) -> None:
        d = ParsedDesign(sections=(), decisions=(), diagnostics=())
        sec = ParsedDesignSection(name="C", body="b", line_start=1, line_end=2)
        with pytest.raises(ValidationError):
            d.sections = (sec,)


class TestParsedTaskListModel:
    def test_frozen_item(self) -> None:
        ti = ParsedTaskItem(text="- [ ] Do it", checked=False,
                            line_number=1, section="S1")
        with pytest.raises(ValidationError):
            ti.text = "changed"

    def test_frozen_list(self) -> None:
        tl = ParsedTaskList(items=(), total=0, completed=0,
                            section_map={}, diagnostics=())
        with pytest.raises(ValidationError):
            tl.total = 99


class TestParseProposalMarkdown:
    def test_standard_proposal(self) -> None:
        text = (
            "## Why\n\nReason.\n\n"
            "## What Changes\n\nChange.\n\n"
            "## Capabilities\n\nCap.\n\n"
            "## Impact\n\nImpact."
        )
        result = parse_proposal_markdown(text)
        assert "Why" in result.sections
        assert "What Changes" in result.sections
        assert "Capabilities" in result.sections
        assert "Impact" in result.sections
        assert result.missing_sections == []
        assert result.unknown_sections == []

    def test_empty_proposal(self) -> None:
        result = parse_proposal_markdown("")
        assert result.sections == {}
        assert len(result.diagnostics) == 1
        assert "empty" in result.diagnostics[0].message.lower()

    def test_unknown_sections_reported(self) -> None:
        text = "## Why\n\nX\n\n## UnknownExtra\n\nY"
        result = parse_proposal_markdown(text)
        assert "UnknownExtra" in result.unknown_sections

    def test_missing_sections_reported(self) -> None:
        text = "## Why\n\nX"
        result = parse_proposal_markdown(text)
        assert "What Changes" in result.missing_sections

    def test_line_ranges(self) -> None:
        text = "## Why\n\nBecause.\n\n## Impact\n\nBig."
        result = parse_proposal_markdown(text)
        assert result.line_ranges["Why"] == (1, 4)
        assert result.line_ranges["Impact"] == (5, 7)


class TestParseDesignMarkdown:
    def test_standard_design(self) -> None:
        text = (
            "## Context\n\nCtx.\n\n"
            "## Decisions\n\n"
            "### D1: Use Python\n\nPython.\n\n"
            "### D2: Use Textual\n\nTextual.\n\n"
            "## Risks\n\nRisk."
        )
        result = parse_design_markdown(text)
        assert len(result.sections) >= 3
        assert len(result.decisions) == 2
        assert result.decisions[0].id == "D1"
        assert result.decisions[1].id == "D2"

    def test_no_decisions(self) -> None:
        text = "## Context\n\nCtx."
        result = parse_design_markdown(text)
        assert len(result.decisions) == 0
        assert any("No decisions" in d.message for d in result.diagnostics)

    def test_decision_without_d_pattern(self) -> None:
        text = (
            "## Decisions\n\n"
            "### NotARealDecision\n\nBody.\n\n"
            "### D1: Good Decision\n\nBody2."
        )
        result = parse_design_markdown(text)
        assert len(result.decisions) == 2
        assert result.decisions[0].id == ""
        assert result.decisions[1].id == "D1"
        assert any("does not match" in d.message.lower() for d in result.diagnostics)

    def test_empty_design(self) -> None:
        result = parse_design_markdown("")
        assert len(result.sections) == 0
        assert len(result.diagnostics) == 1


class TestParseTaskMarkdown:
    def test_standard_tasks(self) -> None:
        text = "## Section 1\n\n- [ ] Task A\n- [x] Task B"
        result = parse_task_markdown(text)
        assert result.total == 2
        assert result.completed == 1
        assert not result.items[0].checked
        assert result.items[1].checked is True

    def test_all_done(self) -> None:
        text = "## S1\n\n- [x] A\n- [X] B"
        result = parse_task_markdown(text)
        assert result.total == 2
        assert result.completed == 2

    def test_empty(self) -> None:
        result = parse_task_markdown("")
        assert result.total == 0
        assert result.completed == 0

    def test_indented_tasks(self) -> None:
        text = "## S1\n\n  - [ ] Indented\n    - [x] Nested"
        result = parse_task_markdown(text)
        assert result.total == 2

    def test_code_block_exclusion(self) -> None:
        text = "## S1\n\nNormal\n\n```\n- [ ] Inside code block\n```\n\n- [x] Outside"
        result = parse_task_markdown(text)
        assert result.total == 1
        assert result.items[0].checked

    def test_section_map(self) -> None:
        text = "## Intro\n\n- [ ] A\n\n## Details\n\n- [x] B\n- [ ] C"
        result = parse_task_markdown(text)
        assert "Intro" in result.section_map
        assert "Details" in result.section_map
        assert result.section_map["Intro"] == (3, 4)
        assert result.section_map["Details"] == (7, 8)

    def test_mixed_checkbox_formats(self) -> None:
        text = "## S1\n\n- [ ] Task A\n- [x] Task B\n-[ ] no space\n* [ ] asterisk"
        result = parse_task_markdown(text)
        assert result.total == 2  # only - [ ] and - [x] with space match
