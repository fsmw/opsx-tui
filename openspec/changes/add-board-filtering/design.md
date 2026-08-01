# Design: add-board-filtering

## Context

- The Changes view already has a text search `Input` (`change-search`) whose `_build_list_items(filter_text)` filters by name substring and always renders an "--- Archived ---" section below active changes.
- The Kanban board (`BoardView.reload()`) groups `workspace.active_changes` by `change.state.value`, sorts, and renders cards; it never shows archived changes and has no filtering.
- `ChangeMetadata` carries `tags: tuple[str, ...]` and `favorite`; `ChangeStatus` carries the 9 lifecycle states. Filtering is purely presentational — it must never mutate change state or persist (docs/05 §18.4: visual metadata does not invalidate verification; board is a projection, not a state machine).
- Hexagonal rules: filtering logic belongs in `domain`/`application` (pure, testable), never inside widgets; `presentation/` must not touch the filesystem.

## Goals / Non-Goals

**Goals**
- One filter model + one pure filter rule usable by both the Changes list and the board.
- Filter by state (multi-select), text (substring on name), tag.
- Show/hide archived toggle, default hidden.
- Visible active-filter indicator and a single "clear filters" action.
- Session-only filter state.

**Non-Goals**
- Persisting filters to disk (deferred; see Open Questions).
- Saved filter presets, complex boolean expressions, regex text filters.
- Filtering specs, tasks, or runs — changes/board only.
- Backend/agent-side filtering.

## Decisions

### D1: Filter model and pure function in the domain layer

New `src/opsx_tui/domain/filtering.py`:

```python
class ChangeFilter(BaseModel, frozen=True):
    states: frozenset[ChangeStatus] = frozenset()   # empty = all states
    text: str = ""
    tags: tuple[str, ...] = ()
    include_archived: bool = False
```

and a pure function:

```python
def filter_changes(changes: Iterable[Change], filt: ChangeFilter) -> tuple[Change, ...]
```

Rules (all AND-ed):
- `states` non-empty → keep only changes whose `state` is in the set.
- `text` non-empty → case-insensitive substring match on `change.name`.
- `tags` non-empty → keep only changes whose metadata has **every** listed tag (AND semantics).
- `include_archived=False` → drop `change.is_archived`; `True` → keep both.
- `filter_changes` never mutates `Change`; returns a new tuple in input order.

Rationale: a single source of truth that both views consume, unit-testable without Textual, and consistent with the existing pure-helper pattern (`lifecycle.assess_lifecycle`, `metadata.merge_metadata`). Alternative considered: filtering logic inside each view → rejected (duplicated rules; spec requires one workspace-filtering contract).

### D2: One shared filter bar widget used by both views

New `src/opsx_tui/presentation/widgets/filter_bar.py`:

```
FilterBar(Widget)
  ├─ Input  (id="filter-text")        # free text; mirrors existing search UX
  ├─ HorizontalScroll (id="filter-states")    # multi-select state chips (Checkboxes)
  ├─ Input/Select (id="filter-tags")  # tag entry (comma-separated or select)
  ├─ Toggle / Checkbox (id="filter-archived")  # "Include archived"
  ├─ Static indicator (id="filter-indicator")   # "N filters" / "no filters"
  └─ Button (id="filter-clear")       # clear all filters
```

`FilterBar` owns the `ChangeFilter` state and emits a custom `FiltersChanged` message carrying the new `ChangeFilter`. Each consumer view (ChangesView, BoardView) registers a handler:

```python
def on_filters_changed(self, event: FilterBar.FiltersChanged) -> None:
    self._active_filter = event.filter
    self._rebuild()          # or self.reload()
```

Rationale: one widget → consistent controls/indicator/clear behavior, no drift between the two views. Alternative: two independent filter implementations → rejected (duplicates the "indicate active filters + clear" logic).

### D3: Text search becomes part of the shared filter

`ChangesView` replaces its bespoke `Input` search with the `FilterBar`; the text field moves into the bar. The existing `test_search_filters` behavior (substring on name) is preserved by the shared `filter_changes` text rule. Board gains the same text field.

Rationale: one text-filter rule (`filter_changes`) instead of the ad-hoc `query in change.name.lower()` inside `_build_list_items`. The Changes view's `Input.Changed` handler is replaced by `FiltersChanged`.

### D4: Board applies filter inside `reload()`

`BoardView.reload()`:
1. Reads `self._active_filter` (default `ChangeFilter()`).
2. Runs `filter_changes(active + archived, filt)`.
3. Groups filtered changes by state; **hides columns when the state filter excludes them** (i.e., if `states` is non-empty, sets `column.display = False` for states not in `states`).
4. `include_archived` renders archived changes into a trailing "Archived" column (title "Archived", state value `archived`), consistent with §23.1 "archived shown separately or via filter".

Rationale: keeps board a pure projection; the state filter maps naturally onto column visibility; archived filter surfaces them separately rather than mixing into active-state columns. Alternative: always show all columns and merely grey out non-matching cards → rejected (noisier; the plan's "filter by state" implies narrowing).

### D5: Active-filter indicator and clear

- `FilterBar` derives `is_active()` from the current `ChangeFilter`: active if any of `states`, `text`, `tags` is non-empty OR `include_archived` is True.
- Indicator shows e.g. `3 active` (or "no filters").
- Clear action resets to `ChangeFilter()` and emits `FiltersChanged`.
- Board's `c` (collapse) binding is unaffected; `clear` is a `FilterBar` control, not a new key binding on the views.

Rationale: matches plan requirement "indicate active filters" / "clear filters" with minimal key-binding surface. Alternative: per-view key bindings (e.g. `/` for text, `f` for filters) → deferred; not needed for this change's scope.

### D6: Session-only state, no persistence

Filter state lives in the in-memory `_active_filter` of each view + `FilterBar`. Nothing is written to disk; restart clears filters.

Rationale: "Optional session persistence" in the plan is explicitly optional; deferring keeps the change small and avoids new config/secrets surface. See Open Questions.

## Risks / Trade-offs

- [Two views drifting in filter behavior] → Mitigation: shared `ChangeFilter` + `filter_changes` (D1) and shared `FilterBar` (D2).
- [Tag filter UX (free text vs select) ambiguous] → Mitigation: free-text comma-separated entry, normalized against known tags; AND semantics. Confirmed testable via `filter_changes`.
- [Board column hiding surprises users] → Mitigation: state filter hides columns only when explicitly chosen; indicator shows active filters; clear restores all.
- [Text search behavior change in ChangesView] → Mitigation: existing `test_search_filters` asserts substring-by-name which the shared rule preserves; update test only if selector changes.
- [FilterBar complexity in narrow terminals] → Mitigation: bar wraps (CSS `wrap`); text input shrinks first; indicator/clear always visible.

## Migration Plan

- Additive: new `domain/filtering.py`, new `presentation/widgets/filter_bar.py`; `changes_view.py` and `board_view.py` modified to consume the shared filter.
- Existing `change-search` Input is replaced by the bar's text field; `on_input_changed` logic removed in favor of `FiltersChanged` handler. Existing tests updated accordingly.
- No data migration, no persistence, no new dependencies.
- Rollback: revert view wiring; `filtering.py`/`filter_bar.py` harmless to keep.

## Open Questions

- **Persistence**: plan marks "optional session persistence". Defer to a later change (likely with config). Confirm.
- **Tag filter input**: free-text comma-separated vs. a select of known tags from the workspace. Design chose free-text (simple, no dependency on a global tag list). Confirm.
- **Board archived column**: show archived as a trailing "Archived" column when `include_archived` is on, vs. only filtering active changes. Design chose the column. Confirm.
