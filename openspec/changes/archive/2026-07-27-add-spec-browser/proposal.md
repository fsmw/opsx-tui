## Why

The Specs tab is currently an empty placeholder with just a label. Users can't browse spec capabilities, inspect requirements and scenarios, search across specs, or see diagnostics. Before the Kanban or change detail screens become useful, users need a way to understand what specs exist in their project and what they require.

## What Changes

- Replace `SpecsView(Widget)` with a full spec browser using a split-panel layout: spec tree on the left, detail panel on the right.
- Tree uses Textual's `Tree` widget showing canonical specs at the top level, expanding to requirements, and further to scenarios.
- Delta specs are shown in a separate section of the tree under "Delta Specs", grouped by parent change.
- Selecting a node shows its detail in the right panel: requirement body + scenarios for a requirement, spec title + diagnostics for a spec.
- Add a search `Input` at the top that filters the tree in real-time, collapsing non-matching nodes.
- Diagnostics (empty specs, malformed requirements) shown as warning markers in the tree and listed in the detail panel.
- Pass `OpenSpecProject` to `SpecsView` via constructor — update `ShellScreen` to pass `self.opsx_project` to all views.
- Spec file path shown in the detail panel, with affordance to open in `$EDITOR` (deferred: just show path).

## Capabilities

### New Capabilities
- `spec-browser`: Tree-based spec browser with requirement/scenario detail, search, and diagnostics.

### Modified Capabilities
- `tui-shell`: Update `ShellScreen` to pass `OpenSpecProject` to all views.
- `project-foundation`: Update `SpecsView` constructor signature.

## Impact

- New files: none (SpecsView is updated in place, no new modules needed unless split-panel logic warrants a dedicated widget file).
- Modified files: `presentation/views/specs_view.py` (full rewrite), `presentation/shell_screen.py` (pass project to views).
- No parser changes needed — `ParsedSpec`, `SpecRequirement`, `SpecScenario` already have the data.
- Does NOT implement: editing specs, `$EDITOR` launch (show path only), cross-spec relationship graph.