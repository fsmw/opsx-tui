from pathlib import Path

import pytest

from opsx_tui.application.config_service import ConfigService
from opsx_tui.domain.config import Config
from opsx_tui.domain.errors import ConfigLoadError
from opsx_tui.domain.logging import Logger


class FakeConfigLoader:
    def __init__(self, config: Config | None = None) -> None:
        self._config = config or Config()

    def load(self) -> Config:
        return self._config


class FailingConfigLoader:
    def load(self) -> Config:
        raise ConfigLoadError(Path("/nonexistent/config.toml"), FileNotFoundError())


class TestConfigService:
    def test_returns_config_from_loader(self) -> None:
        service = ConfigService(loader=FakeConfigLoader())
        config = service.load()
        assert isinstance(config, Config)
        assert config.schema_version == 1

    def test_propagates_load_error(self) -> None:
        service = ConfigService(loader=FailingConfigLoader())
        with pytest.raises(ConfigLoadError):
            service.load()

    def test_accepts_logger(self) -> None:
        messages: list[str] = []

        class CapturingLogger(Logger):
            def info(self, message: str, **kwargs: object) -> None:
                messages.append(message)

            def warning(self, message: str, **kwargs: object) -> None:
                messages.append(message)

            def error(self, message: str, **kwargs: object) -> None:
                messages.append(message)

            def debug(self, message: str, **kwargs: object) -> None:
                messages.append(message)

        service = ConfigService(
            loader=FakeConfigLoader(), logger=CapturingLogger()
        )
        service.load()
        assert any("Configuration loaded" in m for m in messages)
