## 1. Domain models — ChangeMetadata + Priority

- [x] 1.1 Create `Priority(IntEnum)` in `domain/__init__.py` or new `domain/metadata.py` with NORMAL=0, LOW=1, MEDIUM=2, HIGH=3, URGENT=4
- [x] 1.2 Create `ChangeMetadata(BaseModel, frozen=True)` in `domain/metadata.py` with priority, tags, favorite, blocked_reason, notes, order fields
- [x] 1.3 Add `metadata: ChangeMetadata | None = None` field to the `Change` model in `domain/workspace.py`
- [x] 1.4 Verify all existing Change construction sites still work with the new optional field

## 2. MetadataStore Protocol + TomlMetadataStore

- [x] 2.1 Add `MetadataStore(Protocol)` to `domain/ports.py` with `load_all()`, `save()`, `delete()` methods
- [x] 2.2 Create `infrastructure/metadata_store.py` with `_project_key(path)` helper (SHA256 → 12 hex chars)
- [x] 2.3 Implement `TomlMetadataStore.__init__(project_key)` and `load_all()` — reads TOML from platformdirs user_data_dir/metadata/, handles missing file and corrupt TOML gracefully
- [x] 2.4 Implement `TomlMetadataStore.save(change_name, metadata)` — merge in-memory dict, write TOML atomically
- [x] 2.5 Implement `TomlMetadataStore.delete(change_name)` — remove section, write TOML atomically

## 3. Metadata merge service

## 3. Metadata merge service

- [x] 3.1 Create `application/change_metadata_service.py` with pure `merge_metadata(snapshot, metadata_dict)` function
- [x] 3.2 Wire `TomlMetadataStore` and merge call in `application/container.py` — load metadata after workspace scan, merge into snapshot
- [x] 3.3 Integrate merge into `WorkspaceWatcherCallback` so changes are re-merged on workspace refresh

## 4. ChangesView indicators

- [x] 4.1 Update `_format_change_item` in `presentation/views/changes_view.py` to show priority prefix `[H]`/`[U]`, favorite star `★`, and first tag (truncated)
- [x] 4.2 Update `_build_list_items` to sort by `(metadata.order if metadata else 0, name)` ascending
- [x] 4.3 Verify archived "---" divider stays after active changes, before archived

## 5. Overview tab metadata section

- [x] 5.1 Update `_overview_content` in `change_detail_panel.py` to render metadata section when present (priority name, favorite, tags, blocked_reason, notes)
- [x] 5.2 Verify no metadata = no section rendered

## 6. MetadataEditModal

- [x] 6.1 Create `presentation/modals/metadata_edit_modal.py` with `MetadataEditModal(Screen)` containing inputs for tags (comma-separated), notes, blocked_reason, and toggle buttons for priority (cycler 0-4) and favorite
- [x] 6.2 Implement keyboard shortcuts: `f` toggle favorite, `1-4` set priority
- [x] 6.3 Implement save action: calls `MetadataStore.save`, refreshes `ChangesView`
- [x] 6.4 Implement cancel action: Escape discards changes, pops screen
- [x] 6.5 Wire a hotkey in ChangesView (e.g., `e`) to open MetadataEditModal for selected change

## 7. Fixtures

- [x] 7.1 Create `tests/fixtures/metadata/valid.toml` with one change's metadata
- [x] 7.2 Create `tests/fixtures/metadata/empty.toml` (empty file)
- [x] 7.3 Create `tests/fixtures/metadata/malformed.toml` (invalid TOML)

## 8. Tests

- [x] 8.1 Unit test: ChangeMetadata model defaults and invariants
- [x] 8.2 Unit test: Priority IntEnum values
- [x] 8.3 Unit test: Change model backward compat (no metadata)
- [x] 8.4 Unit test: TomlMetadataStore.load_all — empty, valid, malformed
- [x] 8.5 Unit test: TomlMetadataStore.save — creates file, merge preserves unrelated entries
- [x] 8.6 Unit test: TomlMetadataStore.delete — removes section, no-op if missing
- [x] 8.7 Unit test: merge_metadata — pure function, active+archived, no match
- [x] 8.8 Integration test: metadata store round-trip with tmp_path
- [x] 8.9 TUI test: ChangesView indicators render correctly with mock metadata
- [x] 8.10 TUI test: Overview tab shows metadata section
- [x] 8.11 TUI test: MetadataEditModal save/cancel flow
- [x] 8.12 Test all existing tests still pass

## 9. Quality verification

- [x] 9.1 `ruff check .` clean
- [x] 9.2 `mypy src` clean
- [x] 9.3 `pytest` green (all existing + new tests)
