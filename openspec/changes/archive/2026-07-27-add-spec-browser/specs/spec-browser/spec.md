## ADDED Requirements

### Requirement: Split-panel spec browser
The system SHALL provide a `SpecsView` with a split-panel layout: an `Input` search bar at the top, a `Tree` widget for spec navigation on the left (40% width), and a detail panel on the right (60% width) showing content of the selected tree node.

#### Scenario: Split panel renders
- **WHEN** the user switches to the Specs tab
- **THEN** a search input, a spec tree, and a detail panel are visible

#### Scenario: Detail updates on selection
- **WHEN** the user selects a requirement node in the tree
- **THEN** the detail panel shows the requirement body and its scenarios

### Requirement: Spec tree with hierarchy
The tree SHALL show canonical specs at the top level, each expandable to show its requirements, and each requirement expandable to show its scenarios. Delta specs SHALL appear under a "Delta Specs" section, grouped by the change that owns them.

#### Scenario: Tree shows canonical specs
- **WHEN** a project has 3 canonical specs
- **THEN** the tree shows 3 top-level spec nodes plus a "Delta Specs" section

#### Scenario: Requirement expands to scenarios
- **WHEN** the user expands a requirement node
- **THEN** each scenario of that requirement is shown as a child node

#### Scenario: Delta specs grouped by change
- **WHEN** a change with delta specs exists
- **THEN** the delta spec appears under "Delta Specs" → change-name → spec-name

### Requirement: Constructor injection of OpenSpecProject
`SpecsView` SHALL receive `OpenSpecProject` via its constructor. All view widgets (`BoardView`, `SpecsView`, `ChangesView`, `RunView`, `LogsView`, `SettingsView`) SHALL receive `OpenSpecProject` via constructor for consistency.

#### Scenario: SpecsView receives project
- **WHEN** `SpecsView(opsx_project)` is instantiated
- **THEN** `self.opsx_project` contains the project and workspace data

#### Scenario: ShellScreen passes project to all views
- **WHEN** `ShellScreen` composes
- **THEN** every view widget is instantiated with `self.opsx_project`

### Requirement: Search filtering
The `Input` widget at the top SHALL filter the tree in real-time as the user types. Nodes whose label does not contain the search text (case-insensitive) SHALL be hidden. A parent node SHALL remain visible if any of its children match.

#### Scenario: Search hides non-matching specs
- **WHEN** the user types "foundation" in the search input
- **THEN** the spec named "project-foundation" is visible and specs without "foundation" in any descendant node are hidden

#### Scenario: Empty search shows all
- **WHEN** the user clears the search input
- **THEN** all tree nodes are visible

### Requirement: Diagnostic display
Spec nodes with diagnostics SHALL show a warning marker in the tree label. Selecting a spec node SHALL display its diagnostics in the detail panel alongside its requirements.

#### Scenario: Warning marker in tree
- **WHEN** a canonical spec has diagnostics (e.g., empty markdown)
- **THEN** its tree node shows a visual warning indicator

#### Scenario: Diagnostics shown in detail
- **WHEN** the user selects a spec with diagnostics
- **THEN** the detail panel shows a "Diagnostics" section listing each diagnostic message

### Requirement: Detail panel content
The detail panel SHALL display different content depending on the selected tree node type:
- **Spec node**: spec title, file path, full requirements list, diagnostics
- **Requirement node**: requirement name, body text, and each scenario's WHEN/THEN
- **Scenario node**: scenario name, WHEN clause, THEN clause

#### Scenario: Spec detail shows all requirements
- **WHEN** the user selects a spec with 3 requirements
- **THEN** the detail panel shows the spec title and all 3 requirement names and bodies

#### Scenario: Requirement detail shows scenarios
- **WHEN** the user selects a requirement with 2 scenarios
- **THEN** the detail panel shows the requirement body and both scenarios

### Requirement: File path display
The detail panel SHALL show the absolute path of the spec file when a spec node is selected.

#### Scenario: Path displayed
- **WHEN** the user selects a spec node
- **THEN** the detail panel shows "File: /path/to/spec.md"