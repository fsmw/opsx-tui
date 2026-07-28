from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator


class UIConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    show_archived: bool = False
    compact_cards: bool = False
    mouse_support: bool = True


class ExecutionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default_timeout_seconds: int = 1800
    confirm_mutating_operations: bool = True


class BackendConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = "cli"
    executable: str = "codex"
    model: str = "default"
    approval_mode: str = "confirm"


class Config(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int = 1
    default_backend: str = "codex"
    theme: str = "opsx-dark"
    editor: str = "code --wait"
    history_retention_days: int = 90
    ui: UIConfig = UIConfig()
    execution: ExecutionConfig = ExecutionConfig()
    backends: dict[str, BackendConfig] = {}

    @model_validator(mode="after")
    def _reject_secrets(self) -> Config:
        secret_keys = {"api_key", "token", "secret", "password"}
        _check_secrets(self, secret_keys, "")
        return self


def _check_secrets(obj: object, secret_keys: set[str], prefix: str) -> None:
    if isinstance(obj, BaseModel):
        for field_name, field_value in obj:
            full_path = f"{prefix}.{field_name}" if prefix else field_name
            if field_name in secret_keys:
                raise ValueError(
                    f"secrets must not be stored in config: {full_path}"
                )
            _check_secrets(field_value, secret_keys, full_path)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            full_path = f"{prefix}.{key}" if prefix else key
            if key in secret_keys:
                raise ValueError(
                    f"secrets must not be stored in config: {full_path}"
                )
            _check_secrets(value, secret_keys, full_path)
