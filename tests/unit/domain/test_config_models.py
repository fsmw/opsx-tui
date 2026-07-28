import pytest
from pydantic import ValidationError

from opsx_tui.domain.config import Config


class TestConfigDefaults:
    def test_defaults_are_set(self) -> None:
        config = Config()
        assert config.schema_version == 1
        assert config.default_backend == "codex"
        assert config.theme == "opsx-dark"
        assert config.editor == "code --wait"
        assert config.history_retention_days == 90
        assert config.ui.show_archived is False
        assert config.ui.compact_cards is False
        assert config.ui.mouse_support is True
        assert config.execution.default_timeout_seconds == 1800
        assert config.execution.confirm_mutating_operations is True


class TestConfigExtraForbid:
    def test_unknown_top_level_key_raises(self) -> None:
        with pytest.raises(ValidationError):
            Config.model_validate({"unknown_key": "value"})

    def test_unknown_ui_key_raises(self) -> None:
        with pytest.raises(ValidationError):
            Config.model_validate({"ui": {"unknown_ui_field": True}})

    def test_unknown_execution_key_raises(self) -> None:
        with pytest.raises(ValidationError):
            Config.model_validate(
                {"execution": {"unknown_exec_field": "value"}}
            )


class TestConfigRejectSecrets:
    @pytest.mark.parametrize(
        "secret_key",
        ["api_key", "token", "secret", "password"],
    )
    def test_rejects_secret_at_top_level(self, secret_key: str) -> None:
        with pytest.raises(ValidationError):
            Config.model_validate({secret_key: "my-secret-value"})

    @pytest.mark.parametrize(
        "secret_key",
        ["api_key", "token", "secret", "password"],
    )
    def test_rejects_secret_in_backends(self, secret_key: str) -> None:
        with pytest.raises(ValidationError):
            Config.model_validate(
                {"backends": {"codex": {secret_key: "my-secret-value"}}}
            )
