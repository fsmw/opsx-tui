# Design: add-kanban-board

## Context

The Board tab is a placeholder (`BoardView` renders only a centered "Board" label). The workspace already carries everything the board needs to be a pure projection of lifecycle state:

- `WorkspaceSnapshot` with `active_changes` / `archived_changes` (each `Change` has `state: ChangeStatus`, `parsed_tasks`, `artifacts`, `metadata`, `artifact_diagnostics`).
- `ChangeStatus` (9 states) from the `change-lifecycle` change; `Change.state` is already computed by `LifecycleService` in `FilesystemWorkspaceReader`.
- `ChangeMetadata` (priority, tags, favorite, order) merged in by `Container.enrich_snapshot`.
- A watcher: `OpsxTuiApp._on_workspace_change` replaces `self.opsx_project` on workspace changes and calls `self.refresh()`.
- Existing view conventions to reuse: `ChangesView` formats change items (state abbreviation, progress, artifact icons, priority/favorite/tag prefixes) and `ChangeDetailPanel.show_change(change)` renders the detail.

Constraints (binding): the board is a projection, never a state machine (`docs/05` §2.3); cards must NOT be draggable to assign state (§23.4); the board must not store lifecycle state itself; no filesystem/subprocess access from `presentation/`; no new dependencies; no domain logic inside widgets.

## Goals / Non-Goals

**Goals**

- Render a working Kanban board in the Board tab with one column per active lifecycle state.
- Each card shows name, state, task progress, and artifact presence.
- Keyboard navigation: horizontal (between columns) and vertical (within a column).
- Open the existing change detail from a selected card.
- Reactively re-render when the workspace watcher emits a new snapshot.
- Sort within columns; collapse/expand columns; work in narrow terminals.

**Non-Goals**

- Manual card movement / drag-and-drop state assignment (§23.4) — out of scope.
- Archived changes on the board — excluded (shown separately / by filter, per §23.1).
- Filters — deferred to change 3.4 (`add-board-filtering`).
- Editing metadata from the board — already available in ChangesView (`e`).
- Column state persistence — collapsed columns are a transient visual state.

## Decisions

### D1: Column set = the 8 active lifecycle states

Columns map directly to `ChangeStatus` values excluding `archived` and `unknown`:

`draft`, `planning`, `ready`, `applying`, `verification`, `ready-to-archive`, `blocked`.

- `archived` is excluded per §23.1 (separate view / filter).
- `unknown` changes are shown in the `blocked` column? **No.** They are rendered in a final "Unknown" section/column **only if any exist**, per §23.2 ("Unknown column if changes exist"). To keep the board honest, `unknown` gets its own column rendered last when non-empty; when empty the column is omitted.

Rationale: the columns are a projection of the 9-state enum minus archived; hiding empty columns keeps narrow terminals usable. Alternative considered: always render all 9 columns → rejected because an always-empty `unknown` column adds noise and steals horizontal space.

### D2: BoardView is a self-contained widget that rebuilds its DOM

`BoardView` keeps its `opsx_project` reference and exposes a public `reload()` method that:

1. groups `workspace.active_changes` by `change.state.value`;
2. drops the `archived` bucket (never present in active_changes anyway) and creates column widgets in the fixed order above;
3. re-populates each column's cards from the group.

The shell wires `BoardView` already (`shell_screen.py:50`). For reactive refresh, `BoardView` re-reads `self.app.opsx_project` — the app always replaces it before calling `refresh()` in `_on_workspace_change`. Because `reload()` reads the *current* app project rather than a stale constructor copy, the watcher path stays correct.

Rationale: matches the existing `ChangesView` pattern (`_rebuild_list` recreates `ListItem`s) and keeps `presentation/` decoupled from the watcher. Alternative considered: passing the snapshot into the view via constructor each time → requires shell to observe app changes; rejected to avoid cross-widget plumbing.

### D3: DOM shape — columns are vertical scroll containers, cards are Static rows

```
BoardView
└─ Horizontal(id="kanban-board")
   ├─ KanbanColumn (id="column-draft")
   │  ├─ Static(header: "Draft" + count)
   │  └─ VerticalScroll(id="cards-draft")
   │     ├─ KanbanCard  (focusable Static with card markup)
   │     └─ ...
   ├─ KanbanColumn (id="column-planning")
   │  └─ ...
```

- Each `KanbanColumn` is a `Vertical` container with a header `Static` and a `VerticalScroll` of `KanbanCard`s.
- `KanbanCard` extends `Static` and is focusable; focused card shows a distinct style via CSS `:focus`. This gives vertical navigation for free (up/down moves focus within the scroll container; focus follows visible cards) and avoids a per-column `ListView` selection model.
- Horizontal navigation is handled by `BoardView` key bindings: `Left`/`Right` move focus to the previous/next column's first card, `Up`/`Down` move within the current column, `Enter` opens detail.

Rationale: `Static`-based focusable cards give full control over card layout (multi-line progress, icons) that `ListItem` would fight. Alternative considered: one `ListView` per column → simpler selection events but constrains card content and complicates cross-column focus. Rejected.

### D4: Card content = reuse `_format_change_item` conventions

Each card renders, on at most two lines:

- **Line 1**: priority/favorite/tag prefix (same rules as `changes_view._format_change_item`), change name.
- **Line 2**: state abbreviation, task progress `completed/total` (or "no tasks"), artifact indicators (`✓proposal ✓design ✗specs`), and a warning marker when `artifact_diagnostics` is non-empty or the state is `blocked`.

To avoid duplicating formatting rules across widgets, the formatting helpers currently private to `changes_view` (`_STATE_ABBREV`, prefix/icon composition) are extracted into a shared module, e.g. `presentation/views/change_formatting.py`. `ChangesView` is updated to import from it; `KanbanCard` uses the same helpers. This is a refactor, not a behavior change.

Rationale: one formatting source of truth (the lifecycle rules doc demands "rules must not be duplicated between screen and service"). Alternative: leave duplication in the card → rejected (drift risk; the coverage/adapter contract tests treat formatting as part of the change-browser contract).

### D5: Task progress bar

Where `parsed_tasks` is present, the card line shows a compact progress indicator, e.g. `[▓▓░░░] 3/7`, reusing a small pure helper (moved to the shared formatting module). `ParsedTaskList.total == 0` renders `no tasks` (per §17.3, never 0% or 100%). Progress is display-only; never persisted.

### D6: Sorting within a column

Default sort key (per `docs/05` §23.5 order: priority → critical blocks → last modified → name):

1. `metadata.priority` descending (URGENT first);
2. blocked/favorite as a secondary display signal: blocked changes first within their column, then favorite;
3. change name ascending (stable tie-break; "last modified" is not yet modeled on `Change`, see Open Questions).

Rationale: deterministic and uses only fields already on the model. Alternative: sort by `metadata.order` like `ChangesView` → that is the *user-override* ordering; the board keeps priority-first as the documented default and applies `metadata.order` as an additional key when present so user ordering still wins. This is captured in the spec as "sorting is deterministic and configurable".

### D7: Collapsible columns

Pressing `c` toggles the focused column between expanded and collapsed. A collapsed column shows only its header (`Draft (2) ▸`); cards are hidden. Collapse state is an instance attribute on `KanbanColumn` (visual state only — explicitly not persisted, per §18.4 UI filters / visual metadata do not invalidate anything).

### D8: Narrow-terminal adaptation

The board container is a `HorizontalScroll`. Each column has a `min-width` (e.g. 24) but can shrink. On very narrow terminals, columns narrow and card text truncates (Textual `Static` + CSS `overflow`), and the user scrolls horizontally with `Left`/`Right` (or Shift+arrows) to reach columns off-screen. This satisfies "all columns remain reachable via horizontal navigation" (§23 / plan requirement "adapt to narrow terminals").

### D9: Opening detail reuses ChangeDetailPanel

`BoardView` binds `Enter` to open detail. It renders a `ChangeDetailPanel` (id `board-detail-panel`) below the board columns in the same view (Vertical layout: board on top, detail panel at bottom when open), or shows it via the same modal pattern used by `ChangesView`. Design choice: **a modal `Screen`** wrapping `ChangeDetailPanel` (`push_screen`), matching `MetadataEditModal` precedent, so the board doesn't lose layout space. The modal is dismissed with `Escape`. Card selection is preserved on return.

Rationale: reuse the existing detail component untouched (no changes to `change-detail` spec). Alternative: inline detail panel → rejected (squeezes board on narrow terminals).

## Risks / Trade-offs

- [Duplicate formatting logic drifts between ChangesView and cards] → Mitigation: extract shared `change_formatting.py` in this change; both widgets import from it.
- [Focus management across columns is fiddly in Textual] → Mitigation: keep columns as `VerticalScroll` with focusable `Static` cards; Textual handles scroll-into-view on focus; D3 keeps the model minimal.
- [Reactive refresh races (watcher fires during rebuild)] → Mitigation: `reload()` is idempotent and synchronous; rebuilds replace children atomically via `remove_children`+`mount_all`. Widget keying (`id="column-<state>"`) keeps re-mounts stable.
- [Wide boards overflow] → Mitigation: `HorizontalScroll` + `min-width` + horizontal keys (D8). Columns may be collapsed to reclaim space (D7).
- [Card text truncation hides data on narrow terminals] → Mitigation: card shows the most compact single-line summary; full details remain available via `Enter` (D9).

## Migration Plan

- This change is additive: `BoardView` becomes functional; no other view's behavior changes except `ChangesView` importing formatting helpers from the new shared module (verified by existing unit + TUI tests, which must stay green).
- Rollback: `BoardView` reverts to placeholder by removing the new widgets; shared formatting module remains harmless.
- No data migration (no new persistence).

## Open Questions

- **Last-modified sorting**: the `Change` model has no `last_modified` field, yet §23.5 lists it in the default order. Options: (a) add a `last_modified: datetime` to `Change` computed by `FilesystemWorkspaceReader` from artifact mtimes (small domain/reader change), or (b) keep sorting to priority + name + metadata.order for now. Recommended: (b) for this change; revisit if `add-board-filtering` needs it. Confirm during apply.
- **Unknown column**: D1 shows `unknown` only when non-empty. Confirm this matches product intent (vs. always-visible diagnostics column).
