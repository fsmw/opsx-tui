## 1. ChangeDetailPanel widget

- [x] 1.1 Create `presentation/views/change_detail_panel.py` with `ChangeDetailPanel(Widget)` class
- [x] 1.2 Compose `ChangeDetailPanel` with `TabbedContent` and 7 `TabPane` widgets (Overview, Proposal, Design, Specs, Tasks, Runs, Diagnostics)
- [x] 1.3 Implement `show_change(change: Change)` — stores change ref, calls all 7 content builders, updates each tab's `Static` via `.update()`

## 2. Tab content builders

- [x] 2.1 Implement `_overview_content(change)` — name, state, artifact presence, task progress
- [x] 2.2 Implement `_proposal_content(change)` — sections from `parsed_proposal` or "No proposal available"
- [x] 2.3 Implement `_design_content(change)` — decisions from `parsed_design` or "No design available"
- [x] 2.4 Implement `_specs_content(change)` — delta specs list or "No delta specs"
- [x] 2.5 Implement `_tasks_content(change)` — progress bar + task items grouped by section, or "No tasks available"
- [x] 2.6 Implement `_runs_content(change)` — static placeholder text
- [x] 2.7 Implement `_diagnostics_content(change)` — diagnostics + unknown files, or "No diagnostics"

## 3. Update ChangesView

- [x] 3.1 Replace `ScrollableContainer` + `Static(id="detail-content")` with `ChangeDetailPanel` in `ChangesView.compose()`
- [x] 3.2 Update `on_list_view_selected` to call `panel.show_change(change)` instead of building flat content
- [x] 3.3 Remove `ChangeDetailContent.for_change()` static method and `_progress_bar` helper (moved into panel)
- [x] 3.4 Move `_progress_bar` helper into `change_detail_panel.py`

## 4. Tests

- [x] 4.1 Test `ChangeDetailPanel` composes with 7 `TabPane` widgets
- [x] 4.2 Test Overview tab shows change name and state
- [x] 4.3 Test Proposal tab shows sections or missing message
- [x] 4.4 Test Design tab shows decisions or missing message
- [x] 4.5 Test Specs tab shows delta specs or empty message
- [x] 4.6 Test Tasks tab shows progress bar and items or missing message
- [x] 4.7 Test Runs tab shows placeholder text
- [x] 4.8 Test Diagnostics tab shows diagnostics and unknown files
- [x] 4.9 Test `show_change` updates all tabs for a different change
- [x] 4.10 Test ChangesView integrates ChangeDetailPanel and selection updates the panel
- [x] 4.11 Test all existing tests still pass

## 5. Quality verification

- [x] 5.1 Run `ruff check .` and fix issues
- [x] 5.2 Run `mypy src` and fix issues
- [x] 5.3 Run `pytest` — all tests pass with coverage targets met