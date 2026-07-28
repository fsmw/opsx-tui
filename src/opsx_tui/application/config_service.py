from __future__ import annotations

from opsx_tui.domain.config import Config
from opsx_tui.domain.logging import Logger
from opsx_tui.domain.ports import ConfigLoader


class ConfigService:
    def __init__(self, loader: ConfigLoader, logger: Logger | None = None) -> None:
        self._loader = loader
        self._logger = logger

    def load(self) -> Config:
        try:
            config = self._loader.load()
            if self._logger:
                self._logger.info(
                    "Configuration loaded", schema_version=config.schema_version
                )
            return config
        except Exception as e:
            if self._logger:
                self._logger.error("Failed to load configuration", error=str(e))
            raise
