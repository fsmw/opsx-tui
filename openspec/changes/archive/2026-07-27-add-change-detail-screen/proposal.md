## Why

The change detail panel in `ChangesView` currently shows all artifact content as a single flat string with `---` separators. As the amount of parsed data grows (proposal sections, design decisions, delta specs, tasks, diagnostics, future runs), this becomes hard to scan and navigate. A tabbed layout organizes the content into logical sections, letting the user focus on one aspect at a time.

## What Changes

- Extract the detail panel into a standalone `ChangeDetailPanel` widget.
- Replace the `Static` detail content with a `TabbedContent` containing 7 tabs: **Overview**, **Proposal**, **Design**, **Specs**, **Tasks**, **Runs**, **Diagnostics**.
- Each tab shows the corresponding section of the change's parsed data.
- The "Runs" tab is a placeholder (no agent execution yet).
- The panel updates all tabs when a new change is selected.
- Remove `ChangeDetailContent.for_change()` static method (replaced by per-tab builders).
- Add `ChangeDetailPanel` to `ChangesView` in place of the current `ScrollableContainer` + `Static`.

## Capabilities

### New Capabilities
- `change-detail-screen`: Tabbed detail panel inside ChangesView with 7 organized tabs.

### Modified Capabilities
- `change-detail` (from add-change-browser): Replace flat detail with tabs, extract ChangeDetailPanel widget.

## Impact

- New file: `presentation/views/change_detail_panel.py`
- Modified file: `presentation/views/changes_view.py` (use ChangeDetailPanel instead of ScrollableContainer+Static)
- Removed: `ChangeDetailContent.for_change()` static method (logic moves into per-tab builders)
- No changes to domain models
- No changes to other views
- ~10-15 new tests for panel, tabs, content per tab