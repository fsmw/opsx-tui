from __future__ import annotations

import hashlib
import tomllib
from pathlib import Path

from platformdirs import PlatformDirs

from opsx_tui.domain.metadata import ChangeMetadata
from opsx_tui.domain.ports import MetadataStore

_DIRS: PlatformDirs = PlatformDirs("opsx-tui", "opsx-tui")


def _project_key(openspec_root: Path) -> str:
    raw = openspec_root.resolve().absolute().as_posix()
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def _metadata_dir() -> Path:
    return Path(_DIRS.user_data_dir) / "metadata"


def _metadata_path(project_key: str) -> Path:
    return _metadata_dir() / f"{project_key}.toml"


class TomlMetadataStore(MetadataStore):
    def __init__(self, project_key: str) -> None:
        self._project_key = project_key
        self._cache: dict[str, ChangeMetadata] = {}

    def load_all(self) -> dict[str, ChangeMetadata]:
        path = _metadata_path(self._project_key)
        if not path.exists():
            self._cache = {}
            return {}
        try:
            raw = path.read_bytes()
            data = tomllib.loads(raw.decode("utf-8"))
        except Exception:
            self._cache = {}
            return {}
        result: dict[str, ChangeMetadata] = {}
        for name, vals in data.items():
            if not isinstance(vals, dict):
                continue
            result[name] = ChangeMetadata(**vals)
        self._cache = result
        return dict(result)

    def save(self, change_name: str, metadata: ChangeMetadata) -> None:
        self._cache[change_name] = metadata
        self._flush()

    def delete(self, change_name: str) -> None:
        self._cache.pop(change_name, None)
        self._flush()

    def _flush(self) -> None:
        path = _metadata_path(self._project_key)
        _metadata_dir().mkdir(parents=True, exist_ok=True)
        lines: list[str] = []
        for name in sorted(self._cache):
            meta = self._cache[name]
            lines.append(f"[{name}]")
            lines.append(f"priority = {meta.priority.value}")
            if meta.tags:
                tags_repr = ", ".join(f'"{t}"' for t in meta.tags)
                lines.append(f"tags = [{tags_repr}]")
            else:
                lines.append("tags = []")
            lines.append(f"favorite = {'true' if meta.favorite else 'false'}")
            if meta.blocked_reason is not None:
                br = meta.blocked_reason.replace("\\", "\\\\").replace('"', '\\"')
                lines.append(f'blocked_reason = "{br}"')
            if meta.notes is not None:
                n = meta.notes.replace("\\", "\\\\").replace('"', '\\"')
                lines.append(f'notes = "{n}"')
            lines.append(f"order = {meta.order}")
            lines.append("")
        path.write_text("\n".join(lines), encoding="utf-8")
