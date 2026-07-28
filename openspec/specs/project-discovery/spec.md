## ADDED Requirements

### Requirement: CLI argument --project
The system SHALL accept a `--project PATH` CLI argument that specifies the OpenSpec project root. When this argument is provided, the system SHALL bypass all other discovery strategies and validate the given path directly. If the path is invalid, the system SHALL report clear diagnostics and exit or show an error screen.

#### Scenario: --project with valid path
- **WHEN** the user runs `opsx-tui --project /path/to/valid-project`
- **THEN** the app resolves to that project immediately and the discovery chain is skipped

#### Scenario: --project with non-existent path
- **WHEN** the user runs `opsx-tui --project /nonexistent/path`
- **THEN** the app reports that the path does not exist and the discovery source is `cli_arg`

#### Scenario: --project with missing openspec/ dir
- **WHEN** the user runs `opsx-tui --project /path/without-openspec`
- **THEN** the app reports a diagnostic warning that the path lacks an `openspec/` directory

### Requirement: Environment variable OPSX_TUI_PROJECT
The system SHALL read the `OPSX_TUI_PROJECT` environment variable as the second discovery step. If `--project` was not provided and `OPSX_TUI_PROJECT` is set, the system SHALL validate that path. The env var is ignored if `--project` is provided.

#### Scenario: OPSX_TUI_PROJECT set to valid path
- **WHEN** `--project` is not provided and `OPSX_TUI_PROJECT=/path/to/project` is set
- **THEN** the app discovers the project at that path

#### Scenario: OPSX_TUI_PROJECT ignored when --project given
- **WHEN** `--project /explicit` is provided and `OPSX_TUI_PROJECT=/other` is also set
- **THEN** the app discovers the project at `/explicit`

### Requirement: Ancestor directory walk
When `--project` and `OPSX_TUI_PROJECT` are both absent, the system SHALL walk up from the current working directory, looking for an `openspec/` subdirectory in each ancestor. The walk SHALL stop at the first ancestor containing `openspec/` or when 10 levels have been traversed.

#### Scenario: Found via ancestor walk
- **WHEN** cwd is `/home/user/project/src` and `/home/user/project/openspec/` exists
- **THEN** the app discovers the project at `/home/user/project`

#### Scenario: Not found via ancestor walk
- **WHEN** no ancestor directory up to 10 levels contains an `openspec/` subdirectory
- **THEN** the ancestor walk returns `None` and discovery falls to the next strategy

### Requirement: Git root discovery
When ancestor walk returns no result, the system SHALL attempt to discover the project via Git root. It SHALL first try `git rev-parse --show-toplevel`. If `git` is unavailable, it SHALL fall back to walking up looking for a `.git` directory. If the Git root contains an `openspec/` directory, it is returned.

#### Scenario: Found via git rev-parse
- **WHEN** cwd is inside any Git working tree and the root has `openspec/`
- **THEN** the app discovers the project at the Git root

#### Scenario: Found via .git directory walk
- **WHEN** `git` is not installed but a `.git` directory is found in an ancestor
- **THEN** the app discovers the project at the directory containing `.git` if it also has `openspec/`

#### Scenario: Git root without openspec/ is skipped
- **WHEN** the Git root does not contain an `openspec/` directory
- **THEN** the discovery returns `None` and falls to the next strategy

### Requirement: Recent projects discovery
When Git root returns no result, the system SHALL read the recent projects list from `~/.local/share/opsx-tui/recent-projects.json`. Each entry SHALL be validated (path still exists and has `openspec/`). The most recent valid project SHALL be returned.

#### Scenario: Most recent valid project returned
- **WHEN** recent-projects.json has three entries and the most recent path is still valid
- **THEN** the app discovers the project at that path

#### Scenario: All recent projects stale
- **WHEN** recent-projects.json has entries but none of the paths still exist
- **THEN** the app returns `None` and falls to the interactive selector

#### Scenario: Recent projects file missing
- **WHEN** recent-projects.json does not exist
- **THEN** the discovery returns `None` without error

### Requirement: Interactive project picker
When all strategies return `None`, the system SHALL display an interactive screen in the TUI allowing the user to navigate the filesystem and select a directory. The screen SHALL use Textual's `DirectoryTree` widget. When a directory is selected, it SHALL be validated.

#### Scenario: User selects a valid project
- **WHEN** the interactive screen is shown and the user selects a valid project path
- **THEN** the app discovers the project at that path and the project entry is added to recent projects

#### Scenario: User cancels the picker
- **WHEN** the interactive screen is shown and the user presses `Escape`
- **THEN** the app exits cleanly

### Requirement: Project domain model
The system SHALL define a `Project` Pydantic model with fields: `root: Path`, `openspec_root: Path`, `discovery_source: DiscoverySource`, `is_valid: bool`, `diagnostics: tuple[Diagnostic, ...]`. `DiscoverySource` SHALL be a `StrEnum` with values for each step. `Diagnostic` SHALL contain `level: DiagnosticLevel` and `message: str`. The `is_valid` field is set by infrastructure validation based on `openspec/config.yaml` presence (domain does not perform I/O).

#### Scenario: Valid project model
- **WHEN** a path with `openspec/config.yaml` is discovered
- **THEN** the `Project` has `is_valid = True` and no ERROR diagnostics

#### Scenario: Project with warnings
- **WHEN** a path has `openspec/` but is missing `openspec/config.yaml`
- **THEN** the `Project` has `is_valid = False` and a WARNING diagnostic

#### Scenario: Diagnostic levels match
- **WHEN** diagnostics are evaluated
- **THEN** `DiagnosticLevel` values are `INFO`, `WARNING`, `ERROR`

### Requirement: Discovery strategy protocol
The system SHALL define a `ProjectDiscoveryStrategy` Protocol in `domain/` with a single method `discover() -> Project | None`. Each concrete strategy SHALL implement this protocol. Strategies SHALL be stateless (context passed via constructor).

#### Scenario: Strategy returns None for no match
- **WHEN** a strategy finds no matching project
- **THEN** it returns `None` without side effects

#### Scenario: Strategy returns Project for match
- **WHEN** a strategy finds a matching project
- **THEN** it returns a validated `Project` with the correct `DiscoverySource`

### Requirement: Discovery orchestration service
The `ProjectDiscoveryService` in `application/` SHALL accept a `cli_arg: Path | None` and a prioritized list of `ProjectDiscoveryStrategy` instances. It SHALL return `Project | None`. The service SHALL try strategies in order and return the first non-`None` result.

#### Scenario: --project short-circuits
- **WHEN** `cli_arg` is provided
- **THEN** the service validates it directly and does not run any strategy

#### Scenario: Service returns first match
- **WHEN** `cli_arg` is `None` and the second strategy returns a match
- **THEN** the service returns that result and does not try remaining strategies

### Requirement: Recent projects persistence
When a project is successfully discovered and it was not already the most recent entry, the system SHALL append or prepend it to `recent-projects.json`. The file SHALL be capped at 10 entries, with duplicates removed.

#### Scenario: New project added to recent
- **WHEN** a project is discovered manually via interactive picker
- **THEN** its path and current timestamp are added to `recent-projects.json`

#### Scenario: Recent list capped at 10
- **WHEN** the 11th unique project is discovered
- **THEN** the oldest entry is removed before appending the new one

### Requirement: App wiring
`OpsxTuiApp` SHALL accept an optional `project` argument in its constructor. On `mount`, the app SHALL run discovery via `ProjectDiscoveryService`. If a project is found, it SHALL be stored as `self.project` and a placeholder project screen is shown. If not found, `InteractiveProjectScreen` is pushed.

#### Scenario: App stores discovered project
- **WHEN** discovery returns a `Project`
- **THEN** `app.project` is set and the main screen reflects the project root

#### Scenario: Discovery failure shows picker
- **WHEN** discovery returns `None`
- **THEN** `InteractiveProjectScreen` is pushed for user selection
