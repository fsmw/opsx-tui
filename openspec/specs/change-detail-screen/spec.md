# Change Detail Screen

## Purpose

Provides a tabbed detail panel for inspecting a selected OpenSpec change's artifacts: overview, proposal, design, specs, tasks, runs (placeholder), and diagnostics.

## Requirements

### Requirement: Tabbed detail panel
The system SHALL provide a `ChangeDetailPanel` widget with a `TabbedContent` containing 7 tabs: Overview, Proposal, Design, Specs, Tasks, Runs, Diagnostics. Each tab SHALL display content from the selected change's parsed artifacts. The panel SHALL expose a `show_change(change: Change)` method to update all tabs when a different change is selected.

#### Scenario: All 7 tabs present
- **WHEN** a change is selected
- **THEN** the detail panel shows tabs labeled Overview, Proposal, Design, Specs, Tasks, Runs, Diagnostics

#### Scenario: Tabs update on new selection
- **WHEN** the user selects a different change
- **THEN** all tabs update to show the new change's content

### Requirement: Overview tab
The Overview tab SHALL display the change name, state, artifact presence summary, and task progress (if tasks are parsed).

#### Scenario: Overview shows name and state
- **WHEN** a change with parsed data is selected
- **THEN** the Overview tab contains the change name and its `ChangeState`

### Requirement: Proposal tab
The Proposal tab SHALL display all proposal sections (Why, What Changes, Capabilities, Impact) as rendered sections. If `parsed_proposal` is `None`, the tab SHALL show a message indicating the proposal is missing.

#### Scenario: Proposal tab shows sections
- **WHEN** a change with a valid `parsed_proposal` is selected
- **THEN** the Proposal tab shows each section (Why, What Changes, etc.) as a heading followed by its content

#### Scenario: Missing proposal message
- **WHEN** a change has no `parsed_proposal`
- **THEN** the Proposal tab shows "No proposal available"

### Requirement: Design tab
The Design tab SHALL display design decisions. If `parsed_design` is `None`, the tab SHALL show a message indicating the design is missing.

#### Scenario: Design tab shows decisions
- **WHEN** a change has a valid `parsed_design` with decisions
- **THEN** the Design tab lists each decision with its title and body

### Requirement: Specs tab
The Specs tab SHALL list delta specs for the change. If `delta_specs` is empty, the tab SHALL show "No delta specs".

### Requirement: Tasks tab
The Tasks tab SHALL display the task progress bar, task count, and the full task list grouped by section. If `parsed_tasks` is `None`, the tab SHALL show a message indicating tasks are missing.

#### Scenario: Tasks tab shows progress
- **WHEN** a change has `parsed_tasks` with 3 tasks, 2 completed
- **THEN** the Tasks tab shows a progress bar (e.g., `|========>---| 2/3 (66%)`) followed by the task items

### Requirement: Runs tab (placeholder)
The Runs tab SHALL display a static placeholder message indicating that runs will be available in a future version.

### Requirement: Diagnostics tab
The Diagnostics tab SHALL display artifact diagnostics and unknown files found in the change directory. If no diagnostics or unknown files exist, the tab SHALL show "No diagnostics".

#### Scenario: Diagnostics tab shows warnings
- **WHEN** a change has artifact diagnostics
- **THEN** the Diagnostics tab lists each diagnostic with its level and message

#### Scenario: Unknown files listed
- **WHEN** a change directory contains files not recognized as known artifacts
- **THEN** the Diagnostics tab lists them under a "Unknown files" heading
