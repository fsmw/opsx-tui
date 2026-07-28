## Context

The change detail panel inside `ChangesView` (`add-change-browser`) currently uses `ChangeDetailContent.for_change()` to build a single flat string shown in a `Static` widget inside a `ScrollableContainer`. The user needs to scroll through all content to find a specific section. This change organizes the content into 7 tabs.

The existing `ChangesView` is at `presentation/views/changes_view.py` (160 lines). The detail panel is a `Horizontal` split with `ListView` on the left and `ScrollableContainer` containing `Static(id="detail-content")` on the right.

## Goals / Non-Goals

**Goals:**
- Extract a `ChangeDetailPanel` widget with `TabbedContent` and 7 `TabPane` widgets.
- Each tab shows content for its section: Overview, Proposal, Design, Specs, Tasks, Runs, Diagnostics.
- Content is built eagerly when a change is selected (all 7 tabs populated at once).
- The "Runs" tab shows a placeholder message.
- Remove the flat `ChangeDetailContent.for_change()` method.
- Update `ChangesView` to use `ChangeDetailPanel`.

**Non-Goals:**
- No changes to domain models.
- No changes to the change list (left panel) or search.
- No Kanban or lifecycle changes.
- No "Runs" tab functionality (placeholder only — deferred until agent execution exists).

## Decisions

### D1: Extract `ChangeDetailPanel` into its own file
**Choice:** New `presentation/views/change_detail_panel.py` with `ChangeDetailPanel(Widget)`.
**Why:** Keeps `changes_view.py` focused on the list+search+selection logic. The panel has its own compose, content builders, and tab management.
**Alternatives:** Inline the panel in `changes_view.py` — rejected because the file already crosses 150 lines.

### D2: `TabbedContent` for tabs (Textual built-in)
**Choice:** Use Textual's `TabbedContent` with one `TabPane` per section.
**Why:** Consistent with the shell screen pattern, handles focus, click, and keyboard navigation for free.
**Alternatives:** Custom tab bar — rejected as unnecessary duplication.

### D3: Eager content generation on selection
**Choice:** When a change is selected, build content for all 7 tabs at once. Store content in `Static` widgets inside each `TabPane`.
**Why:** Simple, fast (all content is text, no I/O), eliminates lazy-loading complexity. Tab switching becomes instant.
**Alternatives:** Lazy per-tab — rejected as premature optimization for text-only content.

### D4: Per-tab static builder methods
**Choice:** Static methods on `ChangeDetailPanel`: `_overview_content(change)`, `_proposal_content(change)`, etc.
**Why:** Each tab has different rendering logic (progress bar for tasks, decision list for design, icon markers for diagnostics). Separate methods keep each tab's logic isolated.
**Alternatives:** Single `for_change` with if/elif per tab — rejected as harder to test and maintain.

### D5: Runs tab as placeholder
**Choice:** `_runs_content(change)` returns `"No runs yet.\n\nRuns will appear here once agent execution is implemented."`
**Why:** Makes the tab structure future-proof. When agent execution is added, only this method needs updating.
**Alternatives:** Omit the tab — rejected because it would need to be added later as a separate change.

### D6: Update method instead of re-mount
**Choice:** Panel exposes `show_change(change: Change)` that updates all 7 `Static` widgets' content via `.update()`.
**Why:** `mount`/`remove` cycle would flicker. `.update()` is efficient and seamless.
**Alternatives:** Re-mount the panel — rejected as visually disruptive.

## Risks / Trade-offs

- **[Risk] 7 `TabPane` widgets always mounted** → 7 widgets is negligible. Each pane holds a single `Static` child.
- **[Risk] Overview tab duplicates data** → Overview shows change name, state, and high-level summary. Other tabs show detail. This is intentional — the user can scan quickly without clicking through tabs.
- **[Trade-off] Flat `for_change` removed** → Existing code that calls `ChangeDetailContent.for_change()` breaks. Only `ChangesView.on_list_view_selected` uses it, which we update to call `panel.show_change()`.