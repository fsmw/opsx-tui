from opsx_tui.infrastructure.stdlib_logger import Redactor, StdlibLogger


class TestRedactor:
    def test_redacts_known_patterns(self) -> None:
        redactor = Redactor(frozenset({"sk-12345", "ghp_secret"}))
        result = redactor.redact("Token: sk-12345 and key: ghp_secret")
        assert "[REDACTED]" in result
        assert "sk-12345" not in result
        assert "ghp_secret" not in result

    def test_preserves_non_sensitive_text(self) -> None:
        redactor = Redactor(frozenset())
        message = "This is a normal log message"
        assert redactor.redact(message) == message

    def test_case_insensitive_redaction(self) -> None:
        redactor = Redactor(frozenset({"secret-key"}))
        result = redactor.redact("SECRET-KEY is exposed")
        assert "[REDACTED]" in result
        assert "SECRET-KEY" not in result

    def test_empty_patterns_preserves_all(self) -> None:
        redactor = Redactor()
        message = "This contains no redacted content"
        assert redactor.redact(message) == message


class TestStdlibLogger:
    def test_logger_accepts_messages(self) -> None:
        logger = StdlibLogger(name="test-logger")
        logger.info("test info message")
        logger.warning("test warning message")
        logger.error("test error message")
        logger.debug("test debug message")
