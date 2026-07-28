from __future__ import annotations

from pathlib import Path

from opsx_tui.domain.metadata import ChangeMetadata, Priority
from opsx_tui.infrastructure.metadata_store import TomlMetadataStore, _project_key


def test_project_key_deterministic(tmp_path: Path) -> None:
    k1 = _project_key(tmp_path / "project")
    k2 = _project_key(tmp_path / "project")
    assert k1 == k2
    assert len(k1) == 12


def test_project_key_different_for_different_paths(tmp_path: Path) -> None:
    k1 = _project_key(tmp_path / "project-a")
    k2 = _project_key(tmp_path / "project-b")
    assert k1 != k2


def test_load_empty_when_no_file(tmp_path: Path) -> None:
    store = TomlMetadataStore(project_key="test123")
    result = store.load_all()
    assert result == {}


def test_save_and_load(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "opsx_tui.infrastructure.metadata_store._metadata_dir",
        lambda: tmp_path / "metadata",
    )
    store = TomlMetadataStore(project_key="test123")
    meta = ChangeMetadata(priority=Priority.HIGH, tags=("a", "b"), favorite=True)
    store.save("my-change", meta)
    store2 = TomlMetadataStore(project_key="test123")
    loaded = store2.load_all()
    assert "my-change" in loaded
    assert loaded["my-change"].priority == Priority.HIGH
    assert loaded["my-change"].tags == ("a", "b")
    assert loaded["my-change"].favorite is True


def test_save_merge_preserves_unrelated(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "opsx_tui.infrastructure.metadata_store._metadata_dir",
        lambda: tmp_path / "metadata",
    )
    store = TomlMetadataStore(project_key="test123")
    store.save("change-a", ChangeMetadata(priority=Priority.LOW))
    store.save("change-b", ChangeMetadata(priority=Priority.HIGH))
    loaded = store.load_all()
    assert set(loaded.keys()) == {"change-a", "change-b"}


def test_delete_removes_section(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "opsx_tui.infrastructure.metadata_store._metadata_dir",
        lambda: tmp_path / "metadata",
    )
    store = TomlMetadataStore(project_key="test123")
    store.save("change-a", ChangeMetadata())
    store.save("change-b", ChangeMetadata())
    store.delete("change-a")
    loaded = store.load_all()
    assert "change-a" not in loaded
    assert "change-b" in loaded


def test_delete_noop_if_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "opsx_tui.infrastructure.metadata_store._metadata_dir",
        lambda: tmp_path / "metadata",
    )
    store = TomlMetadataStore(project_key="test123")
    store.delete("nonexistent")
    assert store.load_all() == {}


def test_load_corrupt_toml(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "opsx_tui.infrastructure.metadata_store._metadata_dir",
        lambda: tmp_path / "metadata",
    )
    meta_dir = tmp_path / "metadata"
    meta_dir.mkdir(parents=True, exist_ok=True)
    (meta_dir / "test123.toml").write_text("[[broken\ninvalid", encoding="utf-8")
    store = TomlMetadataStore(project_key="test123")
    result = store.load_all()
    assert result == {}
