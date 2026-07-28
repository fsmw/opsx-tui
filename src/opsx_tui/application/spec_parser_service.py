from __future__ import annotations

from opsx_tui.domain.logging import Logger
from opsx_tui.domain.spec_parser import (
    ParsedSpec,
    parse_spec_markdown,
)
from opsx_tui.domain.workspace import CanonicalSpec


class SpecParserService:
    def __init__(self, logger: Logger | None = None) -> None:
        self._logger = logger

    def parse_spec(self, spec: CanonicalSpec) -> ParsedSpec | None:
        spec_file = spec.spec_file
        if spec_file is None:
            return None
        try:
            markdown = spec_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            if self._logger:
                self._logger.warning(f"Spec file not found: {spec_file}")
            return None
        except OSError as e:
            if self._logger:
                self._logger.warning(f"Failed to read spec file {spec_file}: {e}")
            return None
        return parse_spec_markdown(markdown, spec.name)
