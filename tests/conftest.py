from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_environment(tmp_path: Path) -> Iterator[None]:
    original_home = os.environ.get("HOME")
    test_home = tmp_path / "home"
    test_home.mkdir(parents=True, exist_ok=True)
    os.environ["HOME"] = str(test_home)

    for key in list(os.environ):
        if key.startswith("OPSX_TUI_"):
            del os.environ[key]

    yield

    if original_home is not None:
        os.environ["HOME"] = original_home
    else:
        del os.environ["HOME"]
