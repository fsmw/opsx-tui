# Tasks: Add Kanban Board

## 1. Shared formatting helpers

- [x] 1.1 Extract `_STATE_ABBREV` from `changes_view.py` into a new `presentation/views/change_formatting.py` (public constant, unchanged values)
- [x] 1.2 Extract the prefix/icon composition logic of `_format_change_item` into a public `format_change_item(change) -> str` helper in `change_formatting.py`, keeping output identical to current `_format_change_item`
- [x] 1.3 Add a pure `format_progress(parsed_tasks) -> str` helper in `change_formatting.py` producing `[3/7]`-style text, and `no tasks` when total is 0 or tasks are None (never 0% / 100%)
- [x] 1.4 Update `changes_view.py` to import from `change_formatting.py` and re-export `format_change_item` as `_format_change_item` for backward compatibility with existing tests

## 2. Kanban column widget

- [x] 2.1 Create `presentation/views/kanban/kanban_column.py` with `KanbanColumn(Widget)` taking a state name, display title, and accepting child cards
- [x] 2.2 Add header `Static` (title + live card count) and a `VerticalScroll` container (`id="cards-<state>"`) to the column's `compose`
- [x] 2.3 Implement collapse/expand: `action_toggle_collapsed()` toggles a `_collapsed` attribute, hides/shows the cards container, updates header marker; `is_collapsed` property exposed
- [x] 2.4 Add `rebuild(cards: list[KanbanCard])` method that clears and re-mounts cards and updates the header count

## 3. Kanban card widget

- [x] 3.1 Create `presentation/views/kanban/kanban_card.py` with `KanbanCard(Static)` holding the `Change` it represents
- [x] 3.2 Implement card render using `change_formatting` helpers: name + state abbreviation + progress + artifact markers on compact lines, truncated to column width
- [x] 3.3 Add warning/alert marker when `artifact_diagnostics` is non-empty or the change state is `blocked`
- [x] 3.4 Make the card focusable and add a CSS rule (`:focus`) for a distinct focused style

## 4. BoardView implementation

- [x] 4.1 Replace the placeholder `BoardView.compose` with a `HorizontalScroll` (id `kanban-board`) containing one `KanbanColumn` per active state, in fixed order, plus an `Unknown` column only when any change is unknown; `Vertical` wrapper (id `board-layout`)
- [x] 4.2 Implement grouping of `workspace.active_changes` by `change.state.value`; archived changes excluded; add `reload()` that re-reads `self.app.opsx_project` and rebuilds every column
- [x] 4.3 Implement deterministic per-column sorting: `metadata.order` present wins, else priority desc, then blocked first, then favorite, then name asc
- [x] 4.4 Add `reload()` call in `on_mount` so the board renders on tab open
- [x] 4.5 Wire reactive refresh: board re-renders when the workspace watcher delivers a new snapshot (re-reads `self.app.opsx_project`); no manual state mutation
- [x] 4.6 Update `shell_screen.py` BoardView wiring only if the view signature changes (it stays `BoardView(self.opsx_project)`)

## 5. Navigation and detail

- [x] 5.1 Add `BINDINGS` to `BoardView`: Up/Down vertical navigation within a column, Left/Right horizontal navigation between columns (reaching a column's header when it is empty), Enter opens detail, `c` toggles focused column collapse, Escape handled by detail modal
- [x] 5.2 Implement focus movement actions so focus moves between cards in the same column and between columns, with scroll-into-view
- [x] 5.3 Create `presentation/views/kanban/board_detail_modal.py` (or reuse modal pattern) wrapping `ChangeDetailPanel` and pushed via `push_screen`; `Escape` pops it; focus returns to the previously selected card
- [x] 5.4 Wire the `Enter` action to open the detail modal for the focused card's change

## 6. Tests — formatting helpers

- [x] 6.1 Unit tests for `format_change_item`: state abbreviation, progress, priority `[U]`/`[H]`, favorite star, tag truncation, artifact present/missing markers (mirror current `test_changes.py` expectations)
- [x] 6.2 Unit tests for `format_progress`: completed/total rendering, no-tasks handling (total 0 / None → `no tasks`, never 0%/100%)
- [x] 6.3 Update `tests/tui/test_changes.py` imports if needed so existing formatting tests pass against the extracted helper

## 7. Tests — board TUI

- [x] 7.1 `tests/tui/test_board.py`: mount `BoardView` in `run_test` with a fixture project (states spread across columns) and assert a column per active state exists and archived changes are absent
- [x] 7.2 Test unknown column only rendered when an unknown change exists
- [x] 7.3 Test fixed column order (Draft first, Blocked last, Unknown last when present)
- [x] 7.4 Test card rendering: name, state, progress, artifact indicators present on cards
- [x] 7.5 Test sorting: priority desc first, user `metadata.order` override, name tie-break
- [x] 7.6 Test vertical navigation (Up/Down moves focus within column) and horizontal navigation (Left/Right moves between columns; empty adjacent column lands on header)
- [x] 7.7 Test Enter opens detail modal and Escape closes it restoring focus
- [x] 7.8 Test `c` collapses and expands the focused column (cards hidden/restored; header count visible)
- [x] 7.9 Test reactive refresh: swap `app.opsx_project` with a new snapshot (change state changes) and call the watcher callback path, asserting the card moved columns and header counts updated
- [x] 7.10 Test narrow-terminal behavior: board renders in a small `run_test` size and cards truncate without horizontal overflow
- [x] 7.11 Test no manual state assignment: no interaction mutates a change's assessed state

## 8. Quality gates

- [x] 8.1 Run `ruff check .` and fix findings
- [x] 8.2 Run `mypy src` and fix findings
- [x] 8.3 Run full `pytest` suite; all tests green (unit + integration + tui + contract)
- [x] 8.4 Run `/opsx:verify` per DoD; confirm verify is current before any archive step
