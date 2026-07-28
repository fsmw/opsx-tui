## Context

The `ChangesView` is currently a placeholder showing only a label. The `SpecsView` already established a mature split-panel pattern (Input + Tree on left, detail `ScrollableContainer` on right). The change browser follows the same layout philosophy but replaces the `Tree` with a flat `ListView` since changes have a flat structure (no hierarchy). Each change has parsed content via `ParsedProposal`, `ParsedDesign`, `ParsedTaskList` and a deterministic `ChangeState`.

Existing workspace data: `WorkspaceSnapshot.active_changes` and `archived_changes` are `tuple[Change, ...]` with parsed fields already populated by the workspace reader.

## Goals / Non-Goals

**Goals:**
- `ChangesView` with `Input` search + `ListView` (left) + `ScrollableContainer` detail (right).
- Active changes listed first, then archived changes separated by a visual divider.
- Each list item shows: change name, state badge, progress bar (task completion), artifact status icons.
- Detail panel showing proposal, design decisions, tasks, delta specs, diagnostics, and unknown files.
- Search/filter via `Input` that filters the list by name substring (case-insensitive).
- Reactive refresh when `opsx_project` updates (watcher fires).
- Keyboard navigation: up/down for list, `/` for search focus.

**Non-Goals:**
- Markdown rendering (deferred to `add-markdown-preview`).
- Inline editing of change artifacts (read-only browsing).
- Command execution or `openspec` actions (deferred to Fase 4).
- Kanban state inference beyond what `ChangeState` already provides.

## Decisions

### D1: `ListView` over `Tree` for change list
**Choice:** Use Textual's `ListView` with custom `ListItem` children for the change list.
**Why:** Changes are inherently flat (no hierarchy). `ListView` handles up/down navigation natively, provides `highlighted_child` for selected state, and is simpler than a `Tree` with a single level.
**Alternatives:** `Tree` widget — rejected as unnecessary complexity for a flat list. Custom `VerticalScroll` — rejected because `ListView` provides built-in keyboard navigation and selection highlighting.

### D2: Detail content computed from change model fields
**Choice:** A static builder class (like `SpecDetailContent`) that takes a `Change` and returns formatted plain text.
**Why:** Produces deterministic content from frozen models, testable without mounting widgets. Follows the exact pattern established in `SpecsView`.
**Alternatives:** Reactive widgets per section — rejected as over-engineering for a read-only browser.

### D3: Section-aware detail layout
**Choice:** Detail panel sections: Proposal (sections), Design (decisions), Delta Specs, Tasks (progress + item list), Artifact Diagnostics. Each section included only if the corresponding `parsed_*` field is non-None.
**Why:** Keeps detail compact — missing artifacts (e.g., no design.md) don't show empty sections. Clear separation of concerns.
**Alternatives:** One monolithic body — rejected as hard to read. All sections always shown — rejected as noisy for incomplete changes.

### D4: Task progress as visual bar
**Choice:** Render a simple ASCII progress bar (e.g., `[====>----] 5/10 (50%)`) in the detail panel's Tasks section. In the list item, show a compact progress string.
**Why:** Gives immediate visual feedback on completion status. Text-only, no custom `Rich` widgets needed.
**Alternatives:** Textual `ProgressBar` widget — deferred; plain text is simpler and works immediately.

### D5: State badge in list items
**Choice:** Each list item prefix shows the `ChangeState` value as a colored short label (e.g., `[active]`, `[archived]`, `[incomplete]`).
**Why:** Immediate visual identification of change state in the list. Since we don't have TCSS-level coloring yet, the state string itself communicates the status.
**Alternatives:** Color via TCSS classes — deferred as the shell doesn't have a theme system yet.

### D6: Divider between active and archived
**Choice:** Insert a disabled/unselectable separator label between the active-changes group and the archived-changes group in the ListView.
**Why:** Clear visual separation without creating separate views.
**Alternatives:** Two `ListView` widgets in a vertical container — rejected because it complicates single-list keyboard navigation.

### D7: Reactive refresh via `on_mount` + watch
**Choice:** `ChangesView.on_mount` builds the list from `opsx_project.workspace`. On workspace change (watcher fires -> app updates opsx_project -> refreshes screen), `ChangesView` receives a `refresh()` call which triggers `on_mount` re-run.
**Why:** Same pattern as `SpecsView`. Textual's `refresh()` on a widget triggers `compose` re-run, and `on_mount` is called again if the widget is dismounted and remounted. If not, a `watch` can be used.
**Alternatives:** Reactive `self.opsx_project` — the project reference doesn't change identity (it's a new object on each update), so `compose` re-run is the simplest approach.

## Risks / Trade-offs

- **[Risk] Change identity on workspace update** → The `opsx_project.workspace` gets a new snapshot object. `ChangesView` needs to rebuild its list when the project updates. Using `refresh()` (which triggers `compose` re-run) is the simplest path, but may cause flicker. Acceptable for MVP.
- **[Trade-off] Flat list over tree** → Losing hierarchy may make it harder to navigate many changes. With the roadmap capping changes at ~10-20 active at a time, a flat list is acceptable.
- **[Risk] Long change names in list** → `ListView` items may overflow if change names are long. The list width (40%) on an 80-col terminal gives ~32 chars. Long names will be truncated.