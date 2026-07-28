## Context

Specs view is an empty placeholder. `CanonicalSpec.parsed` (ParsedSpec) already has requirements, scenarios, and diagnostics. `WorkspaceSnapshot.specs` holds all canonical specs. Delta specs live in `Change.delta_specs`. The challenge is wiring this data into a navigable, searchable UI.

ShellScreen currently yields `SpecsView()` with no arguments. Views need access to `opsx_project` to render data.

## Goals / Non-Goals

**Goals:**
- Split-panel layout: spec tree (left) + detail panel (right).
- Tree shows canonical specs expanded to requirements → scenarios.
- Search bar filters the tree in real-time.
- Delta specs shown under a "Delta Specs" section, grouped by parent change.
- Diagnostics displayed as warning markers in tree and listed in detail panel.
- `SpecsView` receives `OpenSpecProject` via constructor.
- All views updated to receive `OpenSpecProject` for consistency.

**Non-Goals:**
- Editing specs.
- Opening files in `$EDITOR` (show path only).
- Cross-spec relationship graph.
- Markdown rendering (use plain text for now).
- Sorting/filtering beyond search.

## Decisions

### D1: Split-panel layout (Horizontal)
**Choice:** `SpecsView` uses a horizontal split: `Input` (search) + `Horizontal` with `Tree` (left) and `ScrollableContainer` (detail, right). The tree takes 40% width, detail 60%.
**Why:** Standard browser layout that maximizes both navigation and reading space. 40/60 split gives enough room for the tree while keeping detail readable.
**Alternatives:** Single panel (list → select → detail) — rejected because it requires an extra interaction to see detail. Vertical split — rejected because horizontal gives more room for detail text.

### D2: Textual `Tree` widget for navigation
**Choice:** Use Textual's built-in `Tree` widget. Root node is "Specs" or "Project Specs". Each canonical spec is a child. Each requirement is a child of its spec. Each scenario is a child of its requirement. Delta specs go under a "Delta Specs" section.
**Why:** `Tree` handles expand/collapse, selection, and keyboard navigation natively. Hook `on_tree_node_selected` to update the detail panel.
**Alternatives:** `ListView` — rejected because it can't represent the spec→requirement→scenario hierarchy without nested lists.

### D3: Constructor DI for view data
**Choice:** `SpecsView.__init__(self, opsx_project: OpenSpecProject)`. Update `ShellScreen.compose()` to pass `self.opsx_project` to all views. This is a one-time pattern change that benefits every future view.
**Why:** Clean dependency injection — no globals, no `self.app` coupling, testable in isolation.
**Alternatives:** Access via `self.app.opsx_project` — rejected as implicit coupling. Keep empty constructor — rejected because the view needs data to render.

### D4: Inline delta specs in the tree
**Choice:** After canonical specs, add a "Delta Specs" tree node. Under it, each change with delta specs is a child, and each delta spec expands under its change. Delta spec nodes are styled with a visual marker (e.g., "(delta)" in the label).
**Why:** Keeps canonical and delta specs in one view for cross-referencing. User can see at a glance which changes have pending delta specs.
**Alternatives:** Separate tab for delta specs — rejected as too much navigation for a secondary concern.

### D5: Search filters tree in real-time
**Choice:** `Input` widget at the top. On `on_input_changed`, walk all tree nodes and hide those whose label doesn't match the query text (case-insensitive substring). Matching parent nodes are shown even if the child matches.
**Why:** Instant filtering without a separate search panel. `Input` is a standard Textual widget.
**Alternatives:** Search via command palette (Ctrl+P) — deferred. Search only in detail panel — less useful.

### D6: Diagnostics shown in tree + detail panel
**Choice:** Spec nodes with diagnostics show a visual marker in the tree label (e.g., "Project Foundation ⚠"). Selecting the spec node shows diagnostics in the detail panel as a dedicated section. Selecting a requirement or scenario shows its content only.
**Why:** At-a-glance awareness of spec health in the tree, full details in the panel.
**Alternatives:** Only in detail panel — user must select each spec to see issues. Only in tree — too little context.

### D7: Detail panel shows formatted text, not Markdown
**Choice:** The detail panel is a `Static` or `Label` widget with formatted text: requirement name, body, then each scenario with WHEN/THEN. No Markdown rendering — the construction plan defers Markdown preview to a dedicated change.
**Why:** Plain text works now; Markdown rendering can be swapped in later. The `raw_markdown` field is preserved on `ParsedSpec` for future use.
**Alternatives:** Render Markdown inline with Textual `Markdown` widget — deferred to `add-markdown-preview`.

## Risks / Trade-offs

- **[Risk] `Tree` widget performance with many specs** → Textual's `Tree` is tested for hundreds of nodes. Our spec count is typically under 50. No concern.
- **[Risk] Search filtering tree is jarring** → Nodes disappearing/reappearing as user types may be confusing. Acceptable for MVP; could add match highlighting later.
- **[Trade-off] All views get `opsx_project` in constructor** → One-time change to 5 views + ShellScreen. Some views (like Board, Settings) may not need the data now, but having it available avoids rework.
- **[Risk] Detail panel overflows** → Requirement bodies can be long. Mitigate with `ScrollableContainer`.
- **[Trade-off] No file opening** → Show path only. Opening in `$EDITOR` is a small follow-up.