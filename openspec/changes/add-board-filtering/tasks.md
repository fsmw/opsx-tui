# Tasks: Add Board Filtering

## 1. Domain filtering model

- [x] 1.1 Create `domain/filtering.py` with `ChangeFilter(BaseModel, frozen=True)`: `states: frozenset[ChangeStatus] = frozenset()`, `text: str = ""`, `tags: tuple[str, ...] = ()`, `include_archived: bool = False`
- [x] 1.2 Add pure `filter_changes(changes: Iterable[Change], filt: ChangeFilter) -> tuple[Change, ...]`: AND-ed rules — states non-empty → keep matching state; text non-empty → case-insensitive substring on name; tags non-empty → change must have every tag (tags from change.metadata, missing metadata never matches); `include_archived=False` → drop `is_archived`; preserve input order; never mutate
- [x] 1.3 Add `ChangeFilter.is_active() -> bool` property: True if states/text/tags non-empty OR `include_archived`
- [x] 1.4 Export `ChangeFilter` and `filter_changes` from `domain/__init__.py`

## 2. Unit tests — filtering model

- [x] 2.1 `tests/unit/domain/test_filtering.py`: state single/multi/empty-all scenarios
- [x] 2.2 Text filter: substring match, case-insensitive, empty-shows-all
- [x] 2.3 Tag filter: single tag, multiple tags require all (AND), no-metadata-never-matches
- [x] 2.4 Archive toggle: hidden by default, included when `include_archived=True`
- [x] 2.5 Combined AND: state+text, state+text+tag
- [x] 2.6 `is_active()` truth table and order preservation; filter never mutates input

## 3. FilterBar widget

- [x] 3.1 Create `presentation/widgets/filter_bar.py` with `FiltersChanged` message (carries `filt: ChangeFilter`) defined at module level
- [x] 3.2 `FilterBar(Widget)` compose: `Input#filter-text` (placeholder "Filter..."), `HorizontalScroll#filter-states` (containing `Checkbox` for each state), tag `Input#filter-tags` (comma-separated), archive `Checkbox#filter-archived`, `Static#filter-indicator`, `Button#filter-clear`
- [x] 3.3 `FilterBar` owns its `ChangeFilter` state; text/tag/toggle/state changes update the internal filter and `post_message(FiltersChanged(self, filt))`
- [x] 3.4 `action_clear_filters()` resets to `ChangeFilter()`, updates widgets, posts `FiltersChanged`; indicator reflects `is_active()` ("no filters" vs active count)
- [x] 3.5 Export `FilterBar` from `presentation/widgets/__init__.py`

## 4. ChangesView integration

- [x] 4.1 Replace the bespoke search `Input#change-search` in `changes_view.py` with `FilterBar`
- [x] 4.2 `ChangesView.on_filters_changed(event)`: store `self._active_filter = event.filt`, call `_rebuild_list()` (no longer takes filter_text; filtering delegated to `filter_changes`)
- [x] 4.3 `_build_list_items` calls `filter_changes` separately for `active_changes` and `archived_changes`; "--- Archived ---" header inserted only when the filtered archived list is not empty
- [x] 4.4 Remove `on_input_changed` handler; keep `e` edit_metadata binding and its rebuild callback using current filter

## 5. BoardView integration

- [x] 5.1 Add a `FilterBar` to `BoardView.compose` (above `#kanban-board`)
- [x] 5.2 `BoardView.on_filters_changed(event)`: store filter, `await self.reload()`
- [x] 5.3 `reload()`: run `filter_changes`; group filtered changes by state; when `filt.states` non-empty, set `column.display = False` for excluded states (rather than skipping/unmounting them)
- [x] 5.4 When `filt.include_archived`, dynamically mount a trailing `KanbanColumn("archived", "Archived", id="column-archived")` for archived changes only (and remove it when false, similar to the unknown column)
- [x] 5.5 Text/tag filters hide non-matching cards while leaving columns visible

## 6. TUI tests — FilterBar and integration

- [x] 6.1 `tests/tui/test_filter_bar.py`: compose mounts widgets; text input posts `FiltersChanged` with updated `filt.text`; tag entry parses comma-separated into tuple; archive checkbox toggles `include_archived`; clear resets and posts empty filter; indicator text reflects active state
- [x] 6.2 Update `tests/tui/test_changes.py::test_search_filters` to drive the FilterBar text input (preserve substring-by-name behavior via shared `filter_changes`)
- [x] 6.3 `tests/tui/test_changes.py`: new test that archived header is hidden when archive toggle off and shown when on
- [x] 6.4 `tests/tui/test_board.py`: state filter hides non-matching columns and clearing restores them
- [x] 6.5 `tests/tui/test_board.py`: text filter hides non-matching cards; tag filter keeps only matching cards
- [x] 6.6 `tests/tui/test_board.py`: include_archived renders an Archived column holding only archived changes, absent otherwise
- [x] 6.7 Assert filtering never changes change `state` (data intact across filter/clear)

## 7. Quality gates

- [x] 7.1 Run `ruff check .` and fix findings
- [x] 7.2 Run `mypy src` and fix findings
- [x] 7.3 Run full `pytest` suite; all tests green (unit + integration + tui + contract)
- [x] 7.4 Run `/opsx:verify` per DoD; confirm verify is current before any archive step
