## Why

The ChangesView is currently a placeholder showing just a label. Users can see workspace stats on the board but cannot browse individual changes — their proposals, designs, tasks, progress, or diagnostics. The change-detail screen unlocks the ability to inspect active and archived changes, navigate their artifacts, and understand their state before taking action on them. This is essential before the Kanban board or any command execution can be useful.

## What Changes

- Implement `ChangesView` with a split-panel layout: change list (left) + detail panel (right).
- Show active changes first, then archived ones, separated by a visual divider.
- Display change name, state (inferred), progress bar, and artifact status for each change in the list.
- On selection, show a detail panel with: proposal summary, design decisions, delta specs, task list with progress, artifact diagnostics, and unknown files.
- Add a search/filter input to filter the change list by name or state.
- Wire keyboard navigation: up/down arrows for list, enter for detail, `/` for search.
- Add reactive refresh when the workspace snapshot changes.
- Use constructor DI to receive `OpenSpecProject` (already wired via ShellScreen).
- No Markdown rendering — defer to `add-markdown-preview`; show section-level content as plain text.

## Capabilities

### New Capabilities
- `change-detail`: Change browser with list, detail panel, search/filter, and diagnostics.

### Modified Capabilities
- `tui-shell`: Replaces `ChangesView` placeholder with the full implementation.
- `change-parsing`: Consumed for parsed artifacts (proposal, design, tasks).
- `workspace-catalog`: Consumed for active/archived change listing and metadata.

## Impact

- Modified files: `presentation/views/changes_view.py` (full rewrite from placeholder).
- New files: none (all changes within `changes_view.py` — the entire view is self-contained).
- Does NOT add Markdown rendering — artifact content shown as plain text.
- Does NOT add command execution or agent actions — read-only browsing.
- Depends on `AddChange: parsed_proposal, parsed_design, parsed_tasks, state, artifact_diagnostics` fields already existing.