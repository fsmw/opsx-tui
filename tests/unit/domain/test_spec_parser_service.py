from __future__ import annotations

from pathlib import Path

import pytest

from opsx_tui.application.spec_parser_service import SpecParserService
from opsx_tui.domain.workspace import CanonicalSpec


@pytest.fixture
def service() -> SpecParserService:
    return SpecParserService()


def test_parse_spec_with_valid_fixture(service: SpecParserService) -> None:
    spec = CanonicalSpec(
        name="valid",
        spec_dir=Path("tests/fixtures/spec-parsing/valid"),
        spec_file=Path("tests/fixtures/spec-parsing/valid/spec.md"),
        absolute_spec_dir=Path("tests/fixtures/spec-parsing/valid").resolve(),
        absolute_spec_file=Path("tests/fixtures/spec-parsing/valid/spec.md").resolve(),
    )
    parsed = service.parse_spec(spec)
    assert parsed is not None
    assert parsed.name == "valid"
    assert len(parsed.requirements) == 3


def test_parse_spec_with_nonexistent_file(service: SpecParserService) -> None:
    spec = CanonicalSpec(
        name="nonexistent",
        spec_dir=Path("/nonexistent"),
        spec_file=None,
        absolute_spec_dir=Path("/nonexistent"),
        absolute_spec_file=None,
    )
    parsed = service.parse_spec(spec)
    assert parsed is None


def test_parse_spec_with_nonexistent_path(service: SpecParserService) -> None:
    spec = CanonicalSpec(
        name="ghost",
        spec_dir=Path("/ghost"),
        spec_file=Path("/ghost/spec.md"),
        absolute_spec_dir=Path("/ghost"),
        absolute_spec_file=Path("/ghost/spec.md"),
    )
    parsed = service.parse_spec(spec)
    assert parsed is None
