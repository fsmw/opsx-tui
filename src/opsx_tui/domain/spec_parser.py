from __future__ import annotations

import re

from pydantic import BaseModel

from opsx_tui.domain.project import Diagnostic, DiagnosticLevel


class SpecScenario(BaseModel, frozen=True):
    name: str
    when_clause: str
    then_clause: str
    line_start: int
    line_end: int


class SpecRequirement(BaseModel, frozen=True):
    name: str
    body: str
    scenarios: tuple[SpecScenario, ...]
    line_start: int
    line_end: int


class ParsedSpec(BaseModel, frozen=True):
    name: str
    title: str
    raw_markdown: str
    requirements: tuple[SpecRequirement, ...]
    diagnostics: tuple[Diagnostic, ...]


def name_to_title(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").strip().title()


_SECTION_RE = re.compile(r"^## (ADDED|MODIFIED|REMOVED) Requirements")
_REQUIREMENT_RE = re.compile(r"^### Requirement:\s*(.*)")
_SCENARIO_RE = re.compile(r"^#### Scenario:\s*(.*)")
_WHEN_RE = re.compile(r"^-\s*\*\*WHEN\*\*\s*(.*)")
_THEN_RE = re.compile(r"^-\s*\*\*THEN\*\*\s*(.*)")


def _finalize_scenario(
    req_scenarios: list[SpecScenario],
    current_scenario: SpecScenario | None,
    when_text: str | None,
    then_text: str | None,
    scenario_start_line: int,
    end_line: int,
    diagnostics: list[Diagnostic],
) -> None:
    if current_scenario is None:
        return
    if when_text is None:
        diagnostics.append(Diagnostic(
            level=DiagnosticLevel.INFO,
            message=(
                f"Scenario '{current_scenario.name}' at line"
                f" {scenario_start_line} is missing WHEN clause"
            ),
        ))
    req_scenarios.append(SpecScenario(
        name=current_scenario.name,
        when_clause=when_text or "",
        then_clause=then_text or "",
        line_start=scenario_start_line,
        line_end=end_line,
    ))


def _finalize_requirement(
    requirements: list[SpecRequirement],
    req_name: str,
    req_start_line: int,
    req_scenarios: list[SpecScenario],
    req_body_lines: list[str],
    current_scenario: SpecScenario | None,
    when_text: str | None,
    then_text: str | None,
    scenario_start_line: int,
    end_line: int,
    diagnostics: list[Diagnostic],
) -> tuple[
    str, int, list[SpecScenario], list[str],
    SpecScenario | None, str | None, str | None, int,
]:
    if req_name == "" and req_start_line == 0:
        return (
            req_name, req_start_line, req_scenarios, req_body_lines,
            current_scenario, when_text, then_text, scenario_start_line,
        )

    _finalize_scenario(
        req_scenarios, current_scenario, when_text, then_text,
        scenario_start_line, end_line, diagnostics,
    )
    body = "\n".join(req_body_lines).strip()
    requirements.append(SpecRequirement(
        name=req_name,
        body=body,
        scenarios=tuple(req_scenarios),
        line_start=req_start_line,
        line_end=end_line,
    ))
    return "", 0, [], [], None, None, None, 0


def parse_spec_markdown(markdown: str, spec_name: str) -> ParsedSpec:
    lines = markdown.split("\n")
    diagnostics: list[Diagnostic] = []
    requirements: list[SpecRequirement] = []

    if not markdown.strip():
        diagnostics.append(Diagnostic(
            level=DiagnosticLevel.INFO,
            message="Spec markdown is empty",
        ))
        return ParsedSpec(
            name=spec_name,
            title=name_to_title(spec_name),
            raw_markdown=markdown,
            requirements=(),
            diagnostics=tuple(diagnostics),
        )

    req_name: str = ""
    req_start_line: int = 0
    req_scenarios: list[SpecScenario] = []
    req_body_lines: list[str] = []

    sc_name: str = ""
    scenario_start_line: int = 0
    current_scenario: SpecScenario | None = None
    when_text: str | None = None
    then_text: str | None = None

    for line_no, line in enumerate(lines, 1):
        stripped = line.rstrip()

        section_match = _SECTION_RE.match(stripped)
        if section_match:
            result = _finalize_requirement(
                requirements, req_name, req_start_line, req_scenarios, req_body_lines,
                current_scenario, when_text, then_text, scenario_start_line,
                line_no - 1, diagnostics,
            )
            (req_name, req_start_line, req_scenarios, req_body_lines,
             current_scenario, when_text, then_text, scenario_start_line) = result
            continue

        req_match = _REQUIREMENT_RE.match(stripped)
        if req_match:
            result = _finalize_requirement(
                requirements, req_name, req_start_line, req_scenarios, req_body_lines,
                current_scenario, when_text, then_text, scenario_start_line,
                line_no - 1, diagnostics,
            )
            (req_name, req_start_line, req_scenarios, req_body_lines,
             current_scenario, when_text, then_text, scenario_start_line) = result
            raw_req_name = req_match.group(1).strip()
            if not raw_req_name:
                diagnostics.append(Diagnostic(
                    level=DiagnosticLevel.WARNING,
                    message=f"Requirement at line {line_no} has empty name",
                ))
            req_name = raw_req_name
            req_start_line = line_no
            continue

        sc_match = _SCENARIO_RE.match(stripped)
        if sc_match:
            _finalize_scenario(
                req_scenarios, current_scenario, when_text, then_text,
                scenario_start_line, line_no - 1, diagnostics,
            )
            sc_name = sc_match.group(1).strip()
            scenario_start_line = line_no
            current_scenario = SpecScenario(
                name=sc_name,
                when_clause="",
                then_clause="",
                line_start=line_no,
                line_end=line_no,
            )
            when_text = None
            then_text = None
            continue

        if current_scenario is not None:
            when_match = _WHEN_RE.match(stripped)
            if when_match:
                when_text = when_match.group(1).strip()
                continue
            then_match = _THEN_RE.match(stripped)
            if then_match:
                then_text = then_match.group(1).strip()
                continue

        if req_name:
            req_body_lines.append(line)

    _finalize_requirement(
        requirements, req_name, req_start_line, req_scenarios, req_body_lines,
        current_scenario, when_text, then_text, scenario_start_line,
        len(lines), diagnostics,
    )

    return ParsedSpec(
        name=spec_name,
        title=name_to_title(spec_name),
        raw_markdown=markdown,
        requirements=tuple(requirements),
        diagnostics=tuple(diagnostics),
    )
