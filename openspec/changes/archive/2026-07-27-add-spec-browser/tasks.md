## 1. Pass OpenSpecProject to all views

- [x] 1.1 Update `BoardView.__init__` to accept `opsx_project: OpenSpecProject` and store it
- [x] 1.2 Update `SpecsView.__init__` to accept `opsx_project: OpenSpecProject` and store it
- [x] 1.3 Update `ChangesView.__init__` to accept `opsx_project: OpenSpecProject` and store it
- [x] 1.4 Update `RunView.__init__` to accept `opsx_project: OpenSpecProject` and store it
- [x] 1.5 Update `LogsView.__init__` to accept `opsx_project: OpenSpecProject` and store it
- [x] 1.6 Update `SettingsView.__init__` to accept `opsx_project: OpenSpecProject` and store it
- [x] 1.7 Update `ShellScreen.compose()` to pass `self.opsx_project` to every view instantiation

## 2. Build the spec tree

- [x] 2.1 `SpecsView.on_mount()`: clear default tree, add root "Specs" node
- [x] 2.2 Iterate `self.opsx_project.workspace.specs`: add a `TreeNode` per `CanonicalSpec` with label = spec title (from `ParsedSpec.title` or `name_to_title`), append warning marker if diagnostics exist
- [x] 2.3 For each spec, iterate `parsed.requirements`: add child `TreeNode` per `SpecRequirement` with label = requirement name
- [x] 2.4 For each requirement, iterate `scenarios`: add child `TreeNode` per `SpecScenario` with label = scenario name
- [x] 2.5 After canonical specs, add "Delta Specs" root child node
- [x] 2.6 Iterate `self.opsx_project.workspace.active_changes`: for each change with `delta_specs`, add a change-name child under "Delta Specs", then each delta spec under it

## 3. Detail panel

- [x] 3.1 Add a `ScrollableContainer` (or `Vertical`) to the right side for detail content
- [x] 3.2 Implement `_on_tree_node_selected(event: Tree.NodeSelected)` handler
- [x] 3.3 When a spec node is selected: show spec title, file path, full requirements list, diagnostics section, and raw markdown size
- [x] 3.4 When a requirement node is selected: show requirement name, body text, each scenario with WHEN/THEN
- [x] 3.5 When a scenario node is selected: show scenario name, WHEN, THEN
- [x] 3.6 When delta spec section or change group is selected: show an informational placeholder
- [x] 3.7 Use `Static` widgets for detail content, wrapped in `ScrollableContainer` for overflow

## 4. Search

- [x] 4.1 Add `Input(placeholder="Search specs...")` at the top of `SpecsView`
- [x] 4.2 Implement `on_input_changed` to filter tree: rebuild with only matching nodes (case-insensitive substring on label)
- [x] 4.3 Show parent nodes if any child matches
- [x] 4.4 On empty input, restore all nodes

## 5. Integration

- [x] 5.1 Verify `SpecsView.compose()` has correct TCSS layout: search full-width top, then `Horizontal` with `Tree` 40% + detail 60%
- [x] 5.2 Verify all imports work (Tree, TreeNode, Tree.NodeSelected, Input, Horizontal, Static, ScrollableContainer)

## 6. Tests

- [x] 6.1 Test `SpecsView` receives `opsx_project` and stores it
- [x] 6.2 Test tree is populated with canonical specs from workspace
- [x] 6.3 Test tree shows delta specs under "Delta Specs" group
- [x] 6.4 Test selecting a spec node updates detail with title and path
- [x] 6.5 Test selecting a requirement node shows scenarios
- [x] 6.6 Test search filters tree by text
- [x] 6.7 Test empty search restores all nodes
- [x] 6.8 Test diagnostic warning markers are shown for specs with diagnostics
- [x] 6.9 Test each view widget constructor accepts and stores `opsx_project`
- [x] 6.10 Test all existing tests still pass

## 7. Quality verification

- [x] 7.1 Run `ruff check .` and fix issues
- [x] 7.2 Run `mypy src` and fix issues
- [x] 7.3 Verify all existing tests still pass