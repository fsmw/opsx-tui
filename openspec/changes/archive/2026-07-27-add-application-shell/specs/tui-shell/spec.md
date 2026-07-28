## ADDED Requirements

### Requirement: Shell screen with chrome
The system SHALL provide a `ShellScreen` that hosts the application chrome: a custom header at the top, a tab bar for view switching, a content area for the active view, and a footer showing keyboard bindings. `ShellScreen` SHALL receive `OpenSpecProject` via constructor.

#### Scenario: ShellScreen displays all chrome elements
- **WHEN** `ShellScreen` is mounted
- **THEN** header, tab bar, content area, and footer are visible in the terminal

#### Scenario: ShellScreen receives OpenSpecProject
- **WHEN** `ShellScreen(opsx_project)` is instantiated
- **THEN** `self.opsx_project` contains the project and workspace data

### Requirement: Custom header widget
The system SHALL implement `OpsxHeader` displaying the app name (`OPSX TUI`) on the left, the project root path (truncated if >50 chars) in the center, and the active view name on the right.

#### Scenario: Header shows app name
- **WHEN** `ShellScreen` is mounted
- **THEN** the left side of the header shows `OPSX TUI`

#### Scenario: Header shows project path
- **WHEN** a project is loaded at `/home/user/projects/my-opsx-project`
- **THEN** the center of the header shows the project root path (truncated if necessary)

#### Scenario: Header shows active view
- **WHEN** the user switches to Board view
- **THEN** the right side of the header updates to show `Board`

### Requirement: Tabbed view switching
The system SHALL use Textual's `TabbedContent` with a `TabPane` per view for navigating between 6 views: Board, Specs, Changes, Runner, Logs, Settings. The active tab SHALL be visually highlighted.

#### Scenario: Six views exist as tabs
- **WHEN** `ShellScreen` is composed
- **THEN** tabs for Board, Specs, Changes, Runner, Logs, and Settings are visible in the tab bar

#### Scenario: Clicking a tab switches content
- **WHEN** the user clicks the Specs tab
- **THEN** the Specs content is displayed and the Specs tab is highlighted

### Requirement: Six empty view widgets
The system SHALL provide 6 view widgets — `BoardView`, `SpecsView`, `ChangesView`, `RunView`, `LogsView`, `SettingsView` — each as a `Widget` subclass showing a centered title label matching its name. Views SHALL be located in `presentation/views/`.

#### Scenario: View widget shows its title
- **WHEN** `BoardView` is mounted
- **THEN** it displays the text "Board" centered in the content area

#### Scenario: Each view has its own class
- **WHEN** inspecting the `presentation/views/` module
- **THEN** 6 view classes (`BoardView`, `SpecsView`, `ChangesView`, `RunView`, `LogsView`, `SettingsView`) exist

### Requirement: Keyboard view switching
The keys `1` through `6` SHALL switch to Board, Specs, Changes, Runner, Logs, and Settings views respectively. `q` SHALL quit the application. `?` SHALL open the help modal. `Ctrl+C` SHALL quit the application.

#### Scenario: 1 switches to Board
- **WHEN** the user presses `1`
- **THEN** the Board view becomes active

#### Scenario: q quits the app
- **WHEN** the user presses `q`
- **THEN** the application exits

#### Scenario: ? opens help modal
- **WHEN** the user presses `?`
- **THEN** a help modal overlay appears

### Requirement: Help modal
The system SHALL provide a `HelpModal` screen showing a table of keyboard bindings. The modal SHALL be dismissable by pressing any key.

#### Scenario: Help modal shows bindings
- **WHEN** `HelpModal` is pushed
- **THEN** it displays a table with key bindings (1-6 for views, q for quit, ? for help)

#### Scenario: Any key dismisses help
- **WHEN** the help modal is displayed and the user presses any key
- **THEN** the modal is dismissed and the underlying view is visible

### Requirement: Error modal for critical errors
The system SHALL provide an `ErrorModal` screen that displays an error message and offers the user a choice to continue or exit.

#### Scenario: Error modal shows message
- **WHEN** a critical error occurs and `ErrorModal` is pushed with a message
- **THEN** the modal displays the error text and exit/continue options

### Requirement: Footer with binding hints
The system SHALL include a footer widget (wrapping Textual's `Footer`) at the bottom of the shell that displays available keyboard bindings for the current context.

#### Scenario: Footer shows bindings
- **WHEN** `ShellScreen` is mounted
- **THEN** the footer shows the keyboard bindings (1-6, q, ?, ctrl+c)

### Requirement: App flow updated
`OpsxTuiApp` SHALL push `ShellScreen` instead of `WelcomeScreen` after project discovery and workspace load. `WelcomeScreen` and `InteractiveProjectScreen` SHALL be removed.

#### Scenario: App pushes shell after load
- **WHEN** project discovery and workspace load succeed
- **THEN** `ShellScreen` is pushed with the `OpenSpecProject` instance

#### Scenario: Interactive discovery removed
- **WHEN** `InteractiveProjectScreen` is no longer imported
- **THEN** interactive discovery uses the shell's mechanism (deferred to `discover-openspec-project` change)

### Requirement: Views and widgets directory structure
The system SHALL organize shell code as follows: `presentation/widgets/` for `OpsxHeader`, `OpsxFooter`; `presentation/views/` for the 6 view widgets; `presentation/shell_screen.py` for `ShellScreen`; `presentation/help_modal.py` for `HelpModal`; `presentation/error_modal.py` for `ErrorModal`.

#### Scenario: Directory structure exists
- **WHEN** listing `presentation/widgets/`
- **THEN** `opsx_header.py` and `opsx_footer.py` exist

#### Scenario: View directory exists
- **WHEN** listing `presentation/views/`
- **THEN** 6 view files exist, one per view

### Requirement: No project-screen dependency
The shell SHALL NOT import `project_screen.py`. Starting the app without a valid project SHALL call `self.exit()` with an error notification, not push an interactive screen (interactive discovery will be re-added in a dedicated change).

#### Scenario: No valid project exits cleanly
- **WHEN** no project is discovered via CLI arg, env var, or discovery service
- **THEN** the app shows an error notification and exits