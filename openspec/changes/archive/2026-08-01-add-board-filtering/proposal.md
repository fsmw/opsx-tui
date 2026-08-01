# Proposal: add-board-filtering

## Why

As the workspace grows, the Changes list and Kanban board become unmanageable without narrowing: users need to focus on a subset of changes (by state, by text, by tag) and to keep archived items out of the way. Today only a crude text filter exists in the Changes view (`Input`), and the board has no filtering at all.

## What Changes

- Introduce a shared workspace-filtering capability with a single filter model and a pure filtering rule used by both the Changes view and the Kanban board.
- Filter by state (multi-state selection), by text (case-insensitive substring on change name), and by tag.
- Show/hide archived changes via an explicit toggle (archived hidden by default; the current "--- Archived ---" section in the Changes list respects the toggle).
- Indicate which filters are active and let the user clear all filters with one action.
- Keep filter state in memory for the session (no persistence in this change; see design Open Questions).
- Apply the same filtering to the Kanban board: text/tag/archive filters hide matching cards, and a state filter hides non-matching columns.

## Capabilities

### New Capabilities
- `workspace-filtering`: filter changes and board cards by state, text, and tag; toggle archived visibility; surface and clear active filters.

### Modified Capabilities
<!-- None: filtering is additive; existing specs (changes browser, kanban board) are not re-specified. -->

## Impact

- **New**: `domain/filtering.py` (or under `application/`) — `ChangeFilter` model + pure `filter_changes()` function, unit-tested; contract-tested via adapter contract suite if applicable.
- **Modified**: `presentation/views/changes_view.py` (wire filter controls alongside existing search; archived section respects toggle; active-filter indicator + clear action); `presentation/views/board_view.py` (apply filter in `reload()` grouping).
- **Reused**: `domain/metadata.py` tags, `domain/status.py` ChangeStatus, existing `_STATE_ABBREV`/formatting helpers.
- **No** new dependencies, no filesystem/subprocess from `presentation/`, no persistence, no changes to canonical OpenSpec data.
