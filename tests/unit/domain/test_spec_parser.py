from __future__ import annotations

import pytest
from pydantic import ValidationError

from opsx_tui.domain.project import DiagnosticLevel
from opsx_tui.domain.spec_parser import (
    ParsedSpec,
    SpecRequirement,
    SpecScenario,
    name_to_title,
    parse_spec_markdown,
)


class TestNameToTitle:
    def test_converts_kebab_case(self) -> None:
        assert name_to_title("project-foundation") == "Project Foundation"

    def test_converts_snake_case(self) -> None:
        assert name_to_title("spec_parsing") == "Spec Parsing"

    def test_single_word(self) -> None:
        assert name_to_title("config") == "Config"

    def test_strips_whitespace(self) -> None:
        assert name_to_title("  my-spec  ") == "My Spec"


class TestParseSpecMarkdown:
    def test_valid_spec(self) -> None:
        markdown = (
            "## ADDED Requirements\n\n"
            "### Requirement: Print summary\n"
            "The system SHALL print a summary.\n\n"
            "#### Scenario: No requirements\n"
            "- **WHEN** there are no requirements\n"
            "- **THEN** the summary says empty\n"
        )
        result = parse_spec_markdown(markdown, "test-spec")
        assert result.name == "test-spec"
        assert result.title == "Test Spec"
        assert len(result.requirements) == 1
        assert result.requirements[0].name == "Print summary"
        assert len(result.requirements[0].scenarios) == 1
        assert result.requirements[0].scenarios[0].name == "No requirements"
        s0 = result.requirements[0].scenarios[0]
        assert s0.when_clause == "there are no requirements"
        assert s0.then_clause == "the summary says empty"
        assert result.raw_markdown == markdown

    def test_empty_string(self) -> None:
        result = parse_spec_markdown("", "empty-spec")
        assert len(result.requirements) == 0
        assert len(result.diagnostics) == 1
        assert result.diagnostics[0].level == DiagnosticLevel.INFO
        assert "empty" in result.diagnostics[0].message.lower()

    def test_malformed_scenarios_partial_results(self) -> None:
        markdown = (
            "## ADDED Requirements\n\n"
            "### Requirement: Handle errors\n\n"
            "#### Scenario: Good\n"
            "- **WHEN** something happens\n"
            "- **THEN** it works\n\n"
            "#### Scenario: Broken\n"
            "garbage content\n\n"
            "#### Scenario: Recovered\n"
            "- **WHEN** recovery starts\n"
            "- **THEN** it recovers\n"
        )
        result = parse_spec_markdown(markdown, "malformed")
        req = result.requirements[0]
        assert req.name == "Handle errors"
        assert len(req.scenarios) == 3
        assert req.scenarios[0].name == "Good"
        assert req.scenarios[0].when_clause == "something happens"
        assert req.scenarios[2].name == "Recovered"
        assert req.scenarios[2].when_clause == "recovery starts"

    def test_missing_when_clause(self) -> None:
        markdown = (
            "## ADDED Requirements\n\n"
            "### Requirement: Test\n\n"
            "#### Scenario: Missing when\n"
            "- **THEN** no when here\n"
        )
        result = parse_spec_markdown(markdown, "missing-when")
        req = result.requirements[0]
        assert len(req.scenarios) == 1
        scenario = req.scenarios[0]
        assert scenario.name == "Missing when"
        assert scenario.when_clause == ""
        assert scenario.then_clause == "no when here"
        info_diags = [d for d in result.diagnostics if d.level == DiagnosticLevel.INFO]
        assert len(info_diags) >= 1
        assert "WHEN" in info_diags[0].message

    def test_line_numbers(self) -> None:
        markdown = (
            "## ADDED Requirements\n\n"
            "### Requirement: Test\n"
            "Some body\n\n"
            "#### Scenario: First\n"
            "- **WHEN** x\n"
            "- **THEN** y\n"
        )
        result = parse_spec_markdown(markdown, "lines")
        req = result.requirements[0]
        assert req.line_start == 3
        assert req.scenarios[0].line_start == 6

    def test_raw_markdown_preserved(self) -> None:
        markdown = "## ADDED Requirements\n\n### Requirement: X\n"
        result = parse_spec_markdown(markdown, "preserve")
        assert result.raw_markdown == markdown

    def test_title_from_name(self) -> None:
        result = parse_spec_markdown("## ADDED Requirements\n\n", "project-foundation")
        assert result.title == "Project Foundation"

    def test_empty_requirement_name(self) -> None:
        markdown = (
            "## ADDED Requirements\n\n"
            "### Requirement:\n"
            "Body here\n"
        )
        result = parse_spec_markdown(markdown, "empty-name")
        assert len(result.requirements) == 1
        assert result.requirements[0].name == ""
        warnings = [d for d in result.diagnostics if d.level == DiagnosticLevel.WARNING]
        assert len(warnings) >= 1
        assert "empty name" in warnings[0].message

    def test_multiple_requirements(self) -> None:
        markdown = (
            "## ADDED Requirements\n\n"
            "### Requirement: First\n"
            "#### Scenario: S1\n"
            "- **WHEN** a\n"
            "- **THEN** b\n\n"
            "### Requirement: Second\n"
            "#### Scenario: S2\n"
            "- **WHEN** c\n"
            "- **THEN** d\n"
        )
        result = parse_spec_markdown(markdown, "multi")
        assert len(result.requirements) == 2
        assert result.requirements[0].name == "First"
        assert result.requirements[1].name == "Second"

    def test_removed_section(self) -> None:
        markdown = (
            "## ADDED Requirements\n\n"
            "### Requirement: Added\n"
            "#### Scenario: A\n"
            "- **WHEN** x\n"
            "- **THEN** y\n\n"
            "## REMOVED Requirements\n\n"
            "### Requirement: Removed\n"
            "#### Scenario: R\n"
            "- **WHEN** z\n"
            "- **THEN** w\n"
        )
        result = parse_spec_markdown(markdown, "sections")
        assert len(result.requirements) == 2

    def test_requirement_body_captured(self) -> None:
        markdown = (
            "## ADDED Requirements\n\n"
            "### Requirement: With body\n"
            "First line of body.\n"
            "Second line.\n\n"
            "#### Scenario: Sc\n"
            "- **WHEN** x\n"
            "- **THEN** y\n"
        )
        result = parse_spec_markdown(markdown, "body")
        req = result.requirements[0]
        assert "First line" in req.body
        assert "Second line" in req.body


class TestFrozenModels:
    def test_parsed_spec_frozen(self) -> None:
        spec = ParsedSpec(
            name="test", title="Test",
            raw_markdown="", requirements=(), diagnostics=(),
        )
        with pytest.raises(ValidationError):
            spec.name = "changed"

    def test_requirement_frozen(self) -> None:
        req = SpecRequirement(
            name="R", body="b", scenarios=(),
            line_start=1, line_end=2,
        )
        with pytest.raises(ValidationError):
            req.name = "changed"

    def test_scenario_frozen(self) -> None:
        sc = SpecScenario(
            name="S", when_clause="w", then_clause="t",
            line_start=1, line_end=2,
        )
        with pytest.raises(ValidationError):
            sc.name = "changed"
