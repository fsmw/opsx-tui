## ADDED Requirements

### Requirement: Change list with state and progress
The system SHALL provide a change list within `ChangesView` showing active changes first, then archived changes separated by a visual divider. Each list item SHALL display the change name, its `ChangeState`, task completion progress (e.g., "5/10"), and artifact status indicators for present (✓) and missing (✗) artifacts.

#### Scenario: Active changes listed first
- **WHEN** a workspace has 2 active changes and 1 archived change
- **THEN** the change list shows the 2 active changes first, a divider, then the 1 archived change

#### Scenario: List item shows state badge
- **WHEN** a change is in `ARCHIVED` state
- **THEN** its list item contains the text "archived"

#### Scenario: List item shows progress
- **WHEN** a change has `parsed_tasks.completed=5` and `parsed_tasks.total=10`
- **THEN** its list item contains "5/10"

#### Scenario: Empty changes list
- **WHEN** a workspace has no active or archived changes
- **THEN** the change list shows an informative message ("No changes")

### Requirement: Search filter
The `Input` widget at the top of `ChangesView` SHALL filter the change list in real-time as the user types. Only changes whose name contains the search text (case-insensitive) SHALL remain visible.

#### Scenario: Search filters by name
- **WHEN** the user types "bootstrap" in the search input
- **THEN** only changes whose name contains "bootstrap" are visible

#### Scenario: Empty search shows all
- **WHEN** the search input is empty
- **THEN** all changes are visible

### Requirement: Detail panel for selected change
When a change is selected in the list, the detail panel SHALL show:
- Change name and state
- Proposal sections (Why, What Changes, Capabilities, Impact) if `parsed_proposal` exists
- Design decisions if `parsed_design` exists
- Delta specs list if `delta_specs` is non-empty
- Task list with progress bar and item list if `parsed_tasks` exists
- Artifact diagnostics if `artifact_diagnostics` is non-empty

#### Scenario: Full detail shown
- **WHEN** a change with all artifacts is selected
- **THEN** the detail panel shows Proposal, Design Decisions, Tasks, and Delta Specs sections

#### Scenario: Partial change shows available sections only
- **WHEN** a change missing `design.md` is selected
- **THEN** the detail panel shows Proposal and Tasks but NOT a Design section

#### Scenario: Diagnostics section displayed
- **WHEN** a change has artifact diagnostics
- **THEN** the detail panel shows a Diagnostics section listing each diagnostic message

### Requirement: Task progress bar
The Tasks section in the detail panel SHALL show a visual progress bar (e.g., `[====>----] 5/10 (50%)`) followed by the task list items.

#### Scenario: Progress bar rendered
- **WHEN** a change has 5 completed tasks out of 10 total
- **THEN** the detail shows a progress bar with "5/10 (50%)"

#### Scenario: All tasks completed
- **WHEN** all tasks are checked
- **THEN** the progress bar shows "10/10 (100%)"

### Requirement: Keyboard navigation
`ChangesView` SHALL support keyboard navigation:
- Up/down arrows to move selection in the change list
- Enter to select a change (same as clicking)
- `/` to focus the search input

#### Scenario: Arrow keys move selection
- **WHEN** the user presses down arrow
- **THEN** the next item in the change list is highlighted

#### Scenario: Slash focuses search
- **WHEN** the user presses `/`
- **THEN** the search input receives focus

### Requirement: Reactive refresh on workspace update
`ChangesView` SHALL rebuild its list and detail when the workspace snapshot changes (e.g., via watcher). Stale references to the previous snapshot SHALL NOT be retained.

#### Scenario: New change appears after watcher refresh
- **WHEN** a new change directory is created in `openspec/changes/` while the app is running
- **THEN** the change list updates to show the new change (after the watcher fires)

### Requirement: Unknown files displayed
The detail panel SHALL list any files found in the change directory that are not recognized as known artifacts (proposal.md, design.md, tasks.md). These SHALL be listed under an "Unknown files" section.

#### Scenario: Unknown files shown
- **WHEN** a change directory contains `notes.txt`
- **THEN** the detail panel shows a section listing `notes.txt` as an unknown file

#### Scenario: No unknown files
- **WHEN** a change directory has only recognized artifacts
- **THEN** no "Unknown files" section appears