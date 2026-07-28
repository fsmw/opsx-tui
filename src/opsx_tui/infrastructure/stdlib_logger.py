from __future__ import annotations

import logging
import re
from typing import ClassVar

from opsx_tui.domain.logging import Logger


class Redactor:
    _REDACTED = "[REDACTED]"

    def __init__(self, patterns: frozenset[str] = frozenset()) -> None:
        self._compiled: list[re.Pattern[str]] = [
            re.compile(re.escape(p), re.IGNORECASE) for p in patterns
        ]

    def redact(self, message: str) -> str:
        result = message
        for pattern in self._compiled:
            result = pattern.sub(self._REDACTED, result)
        return result


class RedactingFilter(logging.Filter):
    def __init__(self, redactor: Redactor) -> None:
        super().__init__()
        self._redactor = redactor

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self._redactor.redact(record.msg)
        return True


class StdlibLogger(Logger):
    _DEFAULT_NAME: ClassVar[str] = "opsx_tui"

    def __init__(
        self,
        name: str = _DEFAULT_NAME,
        level: int = logging.INFO,
        redactor: Redactor | None = None,
    ) -> None:
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        if redactor is not None:
            self._logger.addFilter(RedactingFilter(redactor))

    def info(self, message: str, **kwargs: object) -> None:
        self._logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs: object) -> None:
        self._logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs: object) -> None:
        self._logger.error(message, extra=kwargs)

    def debug(self, message: str, **kwargs: object) -> None:
        self._logger.debug(message, extra=kwargs)
