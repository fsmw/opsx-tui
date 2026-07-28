from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from opsx_tui.domain.openspec_cli import CLI_VERSION_MINIMUM, OpenSpecCLIInfo
from opsx_tui.domain.project import Diagnostic, DiagnosticLevel


class TestCLIVersionMinimum:
    def test_constant_value(self) -> None:
        assert CLI_VERSION_MINIMUM == (0, 1, 0)


class TestOpenSpecCLIInfo:
    def test_frozen(self) -> None:
        info = OpenSpecCLIInfo()
        with pytest.raises(ValidationError):
            info.path = None

    def test_default_state(self) -> None:
        info = OpenSpecCLIInfo()
        assert info.path is None
        assert info.version is None
        assert info.version_tuple is None
        assert info.is_compatible is False
        assert info.available_commands == frozenset()
        assert info.diagnostics == ()

    def test_all_fields(self) -> None:
        diag = Diagnostic(level=DiagnosticLevel.INFO, message="ok")
        info = OpenSpecCLIInfo(
            path=Path("/usr/bin/openspec"),
            version="0.2.1",
            version_tuple=(0, 2, 1),
            is_compatible=True,
            available_commands=frozenset({"new", "status"}),
            diagnostics=(diag,),
        )
        assert info.path == Path("/usr/bin/openspec")
        assert info.version == "0.2.1"
        assert info.is_compatible is True
        assert info.available_commands == frozenset({"new", "status"})
        assert info.diagnostics == (diag,)
