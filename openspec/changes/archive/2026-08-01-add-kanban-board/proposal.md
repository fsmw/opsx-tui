# Proposal: add-kanban-board

## Why

The Board tab is currently a placeholder showing only the title "Board". With lifecycle inference in place (every change carries a deterministic `ChangeStatus`), the app needs a projection of the workspace that shows where each change is in its lifecycle at a glance. A Kanban board — columns per lifecycle state, change cards with progress and artifact indicators — is the natural first useful view for phase 3, and it directly satisfies the lifecycle contract's §2.3 (the board is a projection, not a state machine).

## What Changes

- Implement the placeholder `BoardView` as a working Kanban board.
- Add columns for the lifecycle states defined by `change-lifecycle`: Draft, Planning, Ready, Applying, Verification, Ready to Archive, Blocked. Archived changes remain excluded from the active board (they are shown in a separate archived view or via filters, per lifecycle rules §23.1).
- Add a `ChangeCard` widget rendering each change with: name, state abbreviation, task progress, and artifact presence indicators. Cards reuse the formatting conventions already established in `ChangesView` (`_STATE_ABBREV`, priority/favorite/tag prefixes).
- Add horizontal navigation across columns and vertical navigation across cards within a column, with keyboard bindings. An "Open detail" action pushes the existing change detail (via `ChangeDetailPanel`) for the selected change.
- Add reactive refresh: the board re-renders when the workspace watcher emits a new `WorkspaceSnapshot` (the same signal `ChangesView` already consumes).
- Add sorting within each column (default: priority, then critical blocks, then last modified, then name) and make columns collapsible.
- Adapt to narrow terminals: the board SHALL not overflow horizontally; content adapts by layout or column width so all columns remain reachable via horizontal navigation.

## Capabilities

- **New Capabilities**: `kanban-board`
- **Modified Capabilities**: none (the board is a new projection; it does not change the requirements of `change-lifecycle`, `change-metadata`, or `change-detail`).

## Impact

- `src/opsx_tui/presentation/views/board_view.py`: replaced placeholder with the board.
- New files under `src/opsx_tui/presentation/views/kanban/` (or equivalent): board column widget, change card widget, and any shared board layout/format helpers.
- `src/opsx_tui/presentation/views/change_detail_panel.py`: reused as-is for the "Open detail" action; no changes expected.
- `src/opsx_tui/domain/`: no new domain models — the board consumes existing `WorkspaceSnapshot`, `Change`, `ChangeStatus`, `ParsedTaskList`, and `ChangeMetadata`. If a small pure helper (e.g. column ordering or progress formatting) is needed, it lives in `domain/` or `application/`, never in the widget.
- `docs/05-change-lifecycle-rules.md` §23 already defines the board rules (columns, cards, order, no manual state assignment); this change implements that contract.
- No new runtime dependencies. No `shell=True`. No filesystem access from `presentation/` — all data comes from `opsx_project.workspace`.
