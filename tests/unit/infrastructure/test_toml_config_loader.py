from pathlib import Path

import pytest

from opsx_tui.domain.config import Config
from opsx_tui.infrastructure.toml_config_loader import TomlConfigLoader


class TestTomlConfigLoader:
    def test_missing_global_config_returns_defaults(self) -> None:
        loader = TomlConfigLoader(project_root=Path("/nonexistent/project"))
        config = loader.load()
        assert isinstance(config, Config)
        assert config.schema_version == 1

    def test_loads_from_fixture(self, tmp_path: Path) -> None:
        project_dir = tmp_path / "project"
        project_dir.mkdir(parents=True)
        config_dir = project_dir / ".opsx-tui"
        config_dir.mkdir(parents=True)
        toml_path = config_dir / "config.toml"
        toml_path.write_text(
            'theme = "custom-dark"\n'
            'editor = "vim"\n'
            "[ui]\n"
            'show_archived = true\n'
        )

        loader = TomlConfigLoader(project_root=project_dir)
        config = loader.load()
        assert config.theme == "custom-dark"
        assert config.editor == "vim"
        assert config.ui.show_archived is True

    def test_env_overrides_project(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        project_dir = tmp_path / "project"
        project_dir.mkdir(parents=True)
        config_dir = project_dir / ".opsx-tui"
        config_dir.mkdir(parents=True)
        toml_path = config_dir / "config.toml"
        toml_path.write_text(
            "[execution]\n" 'default_timeout_seconds = 1800\n'
        )

        monkeypatch.setenv("OPSX_TUI_EXECUTION__DEFAULT_TIMEOUT_SECONDS", "60")

        loader = TomlConfigLoader(project_root=project_dir)
        config = loader.load()
        assert config.execution.default_timeout_seconds == 60

    def test_missing_project_dir_still_loads_defaults(self) -> None:
        loader = TomlConfigLoader(project_root=Path("/nonexistent/path"))
        config = loader.load()
        assert config.theme == "opsx-dark"
