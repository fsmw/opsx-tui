# OPSX TUI Construction Plan Using OpenSpec

## 1. Purpose of This Document

This document defines the construction phases of **OPSX TUI**, a terminal application developed in Python for viewing, managing, and executing OpenSpec workflows.

The tool will have an interface inspired by applications like `bpytop`, with a Kanban board to visualize changes, specifications, tasks, states, executions, and agent or LLM model providers.

Development will be carried out using OpenSpec as the primary methodology, applying an incremental cycle:

```text
explore → propose → apply → verify → archive
```

Each phase will be divided into small, verifiable changes. When archiving each change, its delta specs will become part of the project's canonical specifications.

---

# 2. Initial Architectural Decisions

## 2.1 Project Identity

| Element | Decision |
|---|---|
| Product name | OPSX TUI |
| PyPI distribution | `opsx-tui` |
| Python package | `opsx_tui` |
| Main command | `opsx-tui` |
| Suggested repository | `opsx-tui` |

## 2.2 Platform and Main Dependencies

| Area | Decision |
|---|---|
| Minimum Python | 3.11 |
| Development Python | 3.14 |
| Target versions | 3.11, 3.12, 3.13, and 3.14 |
| TUI framework | Textual |
| Styles | TCSS |
| Models and validation | Pydantic 2 |
| Async runtime | `asyncio` |
| Process execution | `asyncio.create_subprocess_exec` |
| File watching | `watchfiles` |
| Configuration | TOML |
| System paths | `platformdirs` |
| Operational persistence | SQLite |
| Secrets | Keyring or environment variables |
| Quality | Ruff, MyPy, and Pytest |

## 2.3 Architecture

A lightweight hexagonal architecture will be used:

```text
┌─────────────────────────────────────────┐
│              Presentation               │
│ Textual screens, widgets, controllers   │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│              Application                │
│ Use cases and services                  │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│                Domain                   │
│ Models, rules, and contracts            │
└────────────────────▲────────────────────┘
                     │
┌────────────────────┴────────────────────┐
│            Infrastructure               │
│ Filesystem, CLI, Git, SQLite, agents    │
└─────────────────────────────────────────┘
```

Mandatory rules:

- The interface will not directly access the filesystem.
- The interface will not directly execute subprocesses.
- Models shared across layers will be defined with Pydantic.
- Workspace snapshots will be immutable.
- OpenSpec will be the source of truth for requirements, tasks, and changes.
- OPSX TUI will maintain only operational and presentation data.

---

# 3. Implementation Strategy with OpenSpec

## 3.1 Division Principle

The tool will not be built through a single large proposal.

Each capability will be implemented as an independent OpenSpec change:

```text
/opsx:explore
/opsx:propose
/opsx:apply
/opsx:verify
/opsx:archive
```

Each change must:

1. Have a clear functional objective.
2. Modify a bounded set of capabilities.
3. Have verifiable acceptance criteria.
4. Include tests.
5. Be archived before formally depending on its canonical specs.

## 3.2 General Roadmap States

```text
Phase 0  Project foundation
Phase 1  OpenSpec reading and understanding
Phase 2  TUI shell and navigation
Phase 3  Kanban and lifecycle
Phase 4  OpenSpec command execution
Phase 5  Agent backends
Phase 6  LLM provider configuration
Phase 7  Executions, events, and history
Phase 8  Git, security, and recovery
Phase 9  Distribution and extensibility
```

## 3.3 Main Dependencies

```text
Foundation
    │
    ▼
Project discovery
    │
    ▼
Workspace catalog
    │
    ├──────────────► TUI navigation
    │                       │
    │                       ▼
    ├──────────────► Lifecycle and Kanban
    │
    └──────────────► OpenSpec CLI adapter
                            │
                            ▼
                    Agent backends
                            │
                            ▼
                   Executions and history
                            │
                            ▼
                      Git and security
                            │
                            ▼
                 Distribution and plugins
```

---

# 4. Phase 0 — Project Foundation

## 4.1 Objective

Create the technical and structural foundation of OPSX TUI.

The application should open a minimal Textual interface, load configuration, and expose the `opsx-tui` command.

## 4.2 Exploration

### Suggested Command

```text
/opsx:explore
```

### Instruction

```text
We are starting OPSX TUI, a terminal application in Python to visualize
and operate OpenSpec projects.

Explore the initial architecture considering:

- Python 3.11 as minimum version;
- compatibility with Python 3.11 through 3.14;
- Textual as the only interface framework;
- Pydantic 2 for models and configuration;
- lightweight hexagonal architecture;
- asyncio for concurrency;
- TOML for configuration;
- platformdirs for paths;
- SQLite for future operational persistence;
- keyring or environment variables for secrets;
- Ruff, MyPy, and Pytest.

Do not yet implement OpenSpec reading, Kanban, command execution,
LLM agents, or Git integration.

Deliver decisions, discarded alternatives, risks, and MVP boundaries.
```

## 4.3 Proposal

### Change

```text
bootstrap-opsx-tui-project
```

### Main Spec

```text
project-foundation
```

### Scope

- Package structure.
- Entry point `opsx-tui`.
- Minimal Textual application.
- Simple dependency container.
- Initial configuration models.
- Hierarchical configuration loading.
- Logging.
- Quality tools.
- Unit tests.
- CI for Python 3.11 through 3.14.
- Architecture document.

### Out of Scope

- OpenSpec project reading.
- Kanban.
- Subprocesses.
- Agents.
- Git.
- Functional SQLite.
- LLM providers.

## 4.4 Deliverables

```text
opsx-tui/
├── pyproject.toml
├── src/
│   └── opsx_tui/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       └── presentation/
├── tests/
└── docs/
    └── architecture.md
```

## 4.5 Closing Gate

- `opsx-tui` starts correctly.
- The interface can be closed with the keyboard.
- Global configuration can be loaded.
- Ruff, MyPy, and Pytest pass.
- The CI matrix tests Python 3.11 through 3.14.
- No presentation layer accesses the filesystem.

---

# 5. Phase 1 — OpenSpec Reading and Understanding

## 5.1 Objective

Allow OPSX TUI to detect and represent an OpenSpec project without modifying it.

## 5.2 General Exploration

```text
/opsx:explore
```

```text
Analyze how to detect, read, and represent an OpenSpec project.

Review:

- openspec/config.yaml;
- openspec/specs/;
- openspec/changes/;
- openspec/changes/archive/;
- proposal.md;
- design.md;
- tasks.md;
- delta specs;
- incomplete artifacts;
- differences between filesystem and official CLI.

Determine what should be parsed, what should be queried via OpenSpec CLI,
and what should be treated as Markdown.

Do not yet design the Kanban.
```

---

## 5.3 Change 1.1 — Project Discovery

### Change

```text
discover-openspec-project
```

### Spec

```text
project-discovery
```

### Requirements

- Receive a path via CLI.
- Read `OPSX_TUI_PROJECT`.
- Search for `openspec/` in parent directories.
- Query the Git root as an alternative.
- Validate a minimum structure.
- Report diagnostics.
- Do not create files automatically.
- Do not run `openspec init` without confirmation.

### Algorithm

```text
1. --project
2. OPSX_TUI_PROJECT
3. upward search
4. Git root
5. recent projects
6. interactive selector
```

### Gate

- Correctly detects valid projects.
- Reports incomplete projects.
- Distinguishes "not found" from "invalid structure."

---

## 5.4 Change 1.2 — Workspace Catalog

### Change

```text
read-openspec-workspace
```

### Spec

```text
workspace-catalog
```

### Requirements

- List canonical specs.
- List active changes.
- List archived changes.
- Identify proposal, design, tasks, and delta specs.
- Preserve relative and absolute paths.
- Detect missing artifacts.
- Build an immutable snapshot.
- Do not fail on unknown Markdown.

### Expected Model

```python
class WorkspaceSnapshot(BaseModel):
    root: Path
    specs: tuple[CanonicalSpec, ...]
    active_changes: tuple[Change, ...]
    archived_changes: tuple[Change, ...]
    diagnostics: tuple[Diagnostic, ...]
```

### Gate

- The workspace can be loaded from tests with fixtures.
- The domain does not depend on Textual.
- The parser tolerates incomplete changes.

---

## 5.5 Change 1.3 — Task Parsing

### Change

```text
parse-openspec-tasks
```

### Spec

```text
task-tracking
```

### Requirements

- Recognize `- [ ]`.
- Recognize `- [x]` and `- [X]`.
- Preserve title and line number.
- Recognize identifiers such as `1.1`.
- Preserve grouping by sections.
- Calculate progress.
- Detect ambiguous syntax.
- Do not modify the file.

### Gate

- Correct parsing with simple, nested, and completed tasks.
- Deterministic progress.
- Diagnosis of invalid lines.

---

## 5.6 Change 1.4 — Workspace Watching

### Change

```text
watch-openspec-workspace
```

### Spec

```text
workspace-monitoring
```

### Requirements

- Watch changes under `openspec/`.
- Group repeated events via debounce.
- Detect creation, modification, deletion, and move.
- Refresh only the affected entity.
- Avoid partial states during a write.
- Stop the watcher cleanly.

### Gate

- The application detects external changes.
- The UI does not block.
- No unnecessary refresh cycles are generated.

---

# 6. Phase 2 — TUI Shell and Navigation

## 6.1 Objective

Build the base visual and navigation experience.

## 6.2 Exploration

```text
/opsx:explore
```

```text
Design the experience of a TUI inspired by bpytop for operating OpenSpec.

Define:

- general layout;
- keyboard navigation;
- focus;
- contextual help;
- minimum sizes;
- narrow terminals;
- mouse support;
- modals;
- errors;
- accessibility;
- Markdown rendering.

Do not yet implement Kanban or command execution.
```

---

## 6.3 Change 2.1 — Application Shell

### Change

```text
add-application-shell
```

### Spec

```text
tui-shell
```

### Requirements

- Top bar.
- Central screen area.
- Bottom help bar.
- Navigation between views.
- Focus management.
- Adaptive layout.
- Error modal.
- Clean shutdown.

### Initial Views

```text
Board
Specs
Changes
Runner
Logs
Settings
```

Although some views will be empty, navigation must exist.

---

## 6.4 Change 2.2 — Keyboard Navigation

### Change

```text
add-keyboard-navigation
```

### Spec

```text
keyboard-navigation
```

### Requirements

- Arrow keys.
- `h`, `j`, `k`, `l`.
- Numbers for views.
- `q` to exit.
- `?` for help.
- `/` for search.
- `Ctrl+P` for palette.
- Context-dependent shortcuts.
- Do not intercept keys from editable fields.

---

## 6.5 Change 2.3 — Markdown Viewer

### Change

```text
add-markdown-preview
```

### Spec

```text
markdown-preview
```

### Requirements

- Headings.
- Lists.
- Tables.
- Code blocks.
- Scroll.
- Internal search.
- Open in `$EDITOR`.
- Read errors.
- Non-executable content.

---

## 6.6 Change 2.4 — Spec Browser

### Change

```text
add-spec-browser
```

### Spec

```text
spec-browser
```

### Requirements

- Browse by capability.
- Show requirements and scenarios.
- Search text.
- Show paths.
- Differentiate canonical and delta specs.
- Relate changes to specs.
- Open files in editor.

---

## 6.7 Change 2.5 — Change Detail

### Change

```text
add-change-detail-screen
```

### Spec

```text
change-detail
```

### Requirements

- Show proposal.
- Show design.
- Show delta specs.
- Show tasks.
- Show progress.
- Show missing artifacts.
- Show diagnostics.
- Update on filesystem changes.

### Phase Gate

- The user can open a project.
- They can navigate specs and changes.
- They can review artifacts without leaving the TUI.
- No commands are executed yet.

---

# 7. Phase 3 — Lifecycle and Kanban Board

## 7.1 Objective

Transform real OpenSpec artifacts into a Kanban visualization.

## 7.2 Principle

The board will not be a parallel source of state.

```text
OpenSpec = methodological source of truth
OPSX TUI = visual projection and operational state
```

## 7.3 Exploration

```text
/opsx:explore
```

```text
Design a lifecycle model for OpenSpec changes that can be projected
onto a Kanban.

State should be derived from:

- existing artifacts;
- tasks;
- archive status;
- validations;
- verification results;
- action availability.

Columns must not become mandatory phases.

Define states, rules, reasons, and block handling.
```

---

## 7.4 Change 3.1 — Lifecycle Inference

### Change

```text
infer-change-lifecycle
```

### Spec

```text
change-lifecycle
```

### Initial States

```text
draft
planning
ready
applying
verification
ready-to-archive
blocked
archived
```

### Requirements

- Deterministic state.
- Visible reasons.
- Available actions.
- Do not write calculated state into OpenSpec.
- Invalidate verification when relevant artifacts change.
- Allow local operational blocking.
- Use official state when available.

### Expected Model

```python
class LifecycleAssessment(BaseModel):
    status: ChangeStatus
    reasons: tuple[str, ...]
    available_actions: tuple[str, ...]
    warnings: tuple[str, ...]
```

---

## 7.5 Change 3.2 — Kanban Board

### Change

```text
add-kanban-board
```

### Spec

```text
kanban-board
```

### Requirements

- Columns by state.
- Change cards.
- Task progress.
- Artifact indicators.
- Horizontal and vertical navigation.
- Open detail.
- Adapt to narrow terminals.
- Reactive refresh.
- Sorting.
- Collapsible columns.

---

## 7.6 Change 3.3 — Local Metadata

### Change

```text
add-local-change-metadata
```

### Spec

```text
change-metadata
```

### Allowed Data

- Priority.
- Tags.
- Local block reason.
- Favorites.
- Visual order.
- Operational notes.

### Disallowed Data

- Duplicate progress.
- Duplicate archived status.
- Copies of specs.
- Copies of `tasks.md`.
- Inferred state persisted as truth.

---

## 7.7 Change 3.4 — Search and Filters

### Change

```text
add-board-filtering
```

### Spec

```text
workspace-filtering
```

### Requirements

- Filter by state.
- Filter by text.
- Filter by tag.
- Show or hide archived.
- Indicate active filters.
- Clear filters.
- Optional session persistence.

### Phase Gate

The tool already fulfills its first useful objective:

> Visualize specs, changes, progress, and OpenSpec states from a terminal board.

---

# 8. Phase 4 — OpenSpec Command Execution

## 8.1 Objective

Allow the TUI to execute local OpenSpec commands securely.

## 8.2 Exploration

```text
/opsx:explore
```

```text
Analyze current OpenSpec commands and OPSX actions.

Classify each operation as:

1. local CLI command;
2. action requiring an agent;
3. hybrid operation;
4. informational operation.

Design a versionable catalog and avoid coupling the interface to a single
version of OpenSpec.
```

---

## 8.3 Change 4.1 — CLI Adapter

### Change

```text
add-openspec-cli-adapter
```

### Spec

```text
openspec-cli
```

### Requirements

- Detect executable.
- Get version.
- Execute with separated arguments.
- Do not use `shell=True`.
- Configure `cwd`.
- Capture stdout and stderr.
- Capture exit code.
- Timeout.
- Cancellation.
- Diagnostics.
- Version compatibility.

---

## 8.4 Change 4.2 — Command Catalog

### Change

```text
add-command-catalog
```

### Spec

```text
command-catalog
```

### Requirements

Each operation must declare:

- Identifier.
- Label.
- Executor type.
- Parameters.
- Whether it needs a change.
- Whether it modifies files.
- Whether it needs confirmation.
- Compatibility.
- Unavailability reason.

---

## 8.5 Change 4.3 — Command Palette

### Change

```text
add-command-palette
```

### Spec

```text
command-palette
```

### Requirements

- Search actions.
- Filter by context.
- Show risks.
- Show backend.
- Request parameters.
- Execute via keyboard.
- Show disabled actions with explanation.

---

## 8.6 Change 4.4 — OpenSpec Runner

### Change

```text
add-openspec-command-runner
```

### Spec

```text
command-execution
```

### Requirements

- Preview.
- Confirmation.
- Streaming.
- Cancellation.
- Timeout.
- One modifying execution per workspace.
- Subsequent refresh.
- Basic logging.
- Non-blocking interface.

### Phase Gate

- OPSX TUI executes local OpenSpec commands.
- The user sees command, output, and result.
- Actions requiring agents are not yet executed.

---

# 9. Phase 5 — Agent Backends

## 9.1 Objective

Allow OPSX TUI to invoke programming agents to execute OPSX actions.

The first backend will be Codex CLI.

## 9.2 Exploration

```text
/opsx:explore
```

```text
Explore how to abstract programming agents executed from CLI.

The first backend will be Codex CLI.

The architecture should allow later addition of:

- Claude Code;
- Gemini CLI;
- other agents.

Define:

- healthcheck;
- capabilities;
- model selection;
- sandbox;
- approvals;
- streaming;
- cancellation;
- errors;
- normalized results;
- differences between agents.
```

---

## 9.3 Change 5.1 — Backend Contract

### Change

```text
define-agent-backend-contract
```

### Spec

```text
agent-backend
```

### Requirements

- Identification.
- Healthcheck.
- Capability list.
- Async execution.
- Event streaming.
- Cancellation.
- Model.
- Approvals.
- Sandbox.
- Working directory.
- Normalized result.

---

## 9.4 Change 5.2 — Codex Backend

### Change

```text
add-codex-cli-backend
```

### Spec

```text
codex-backend
```

### Requirements

- Detect Codex CLI.
- Verify authentication.
- Select model.
- Execute in the workspace.
- Configure sandbox.
- Configure approvals.
- Capture events.
- Cancel.
- Do not store credentials.

---

## 9.5 Change 5.3 — OPSX Orchestration

### Change

```text
execute-opsx-actions-through-agent
```

### Spec

```text
opsx-orchestration
```

### Initial Actions

```text
explore
propose
apply
verify
sync
archive
```

### Requirements

- Build a clear instruction.
- Associate the action with the change.
- Show prompt before executing.
- Refresh the workspace during execution.
- Detect modified artifacts.
- Validate the result via filesystem or CLI.
- Do not trust only the agent's text output.

---

## 9.6 Change 5.4 — Agent Profiles

### Change

```text
add-agent-profile-settings
```

### Spec

```text
agent-configuration
```

### Requirements

- Default backend.
- Backend per operation.
- Model per operation.
- Timeout.
- Sandbox.
- Approvals.
- Allowed environment variables.
- Global and per-project configuration.
- Availability check.

### Phase Gate

The TUI can execute a complete flow through Codex:

```text
propose → apply → verify → archive
```

---

# 10. Phase 6 — Direct LLM Providers

## 10.1 Objective

Add optional support for LLM providers that are not executed as CLI agents.

This phase is outside the initial MVP.

## 10.2 Exploration

```text
/opsx:explore
```

```text
Evaluate the incorporation of direct LLM providers.

Consider:

- OpenAI-compatible;
- OpenAI;
- OpenRouter;
- LM Studio;
- Ollama;
- Anthropic;
- Gemini;
- Azure OpenAI.

Determine which operations can be performed without a full code agent,
which tools the model should receive, and how to limit its system access.
```

---

## 10.3 Change 6.1 — Provider Registry

### Change

```text
add-provider-registry
```

### Spec

```text
llm-provider-registry
```

### Requirements

- Register providers.
- Declare capabilities.
- Configure endpoint.
- Configure model.
- Test connection.
- Select provider per operation.

---

## 10.4 Change 6.2 — OpenAI Compatible

### Change

```text
add-openai-compatible-provider
```

### Spec

```text
openai-compatible-provider
```

### Initial Coverage

- OpenAI.
- OpenRouter.
- LM Studio.
- Compatible Ollama.
- Compatible private endpoints.

---

## 10.5 Change 6.3 — Credential Management

### Change

```text
add-secure-credential-storage
```

### Spec

```text
credential-management
```

### Requirements

- Keyring.
- Environment variables.
- Do not save keys in TOML.
- Hide values.
- Redact logs.
- Delete credentials.
- Test credentials without exposing them.

---

# 11. Phase 7 — Executions, Events, and History

## 11.1 Objective

Create an observable and persistent model for each execution.

## 11.2 Exploration

```text
/opsx:explore
```

```text
Design the observable execution model for OPSX TUI.

Each execution must record:

- operation;
- change;
- backend;
- model;
- start and end;
- events;
- stdout and stderr;
- affected files;
- result;
- cancellation;
- recovery.

Define persistence, rotation, limits, and auditing.
```

---

## 11.3 Change 7.1 — Event Model

### Change

```text
add-execution-event-model
```

### Spec

```text
execution-events
```

### Initial Events

```text
execution.started
process.spawned
output.received
artifact.created
artifact.modified
task.completed
validation.started
validation.completed
execution.cancelled
execution.failed
execution.completed
```

---

## 11.4 Change 7.2 — Live Console

### Change

```text
add-live-execution-console
```

### Spec

```text
execution-console
```

### Requirements

- Streaming.
- Scroll.
- Auto-follow.
- Pause.
- Search.
- Cancellation.
- Status.
- Duration.
- Bounded memory.

---

## 11.5 Change 7.3 — Persistent History

### Change

```text
persist-execution-history
```

### Spec

```text
execution-history
```

### Persistence

SQLite at:

```text
~/.local/share/opsx-tui/opsx-tui.db
```

### Data

- Project.
- Change.
- Operation.
- Backend.
- Model.
- Timestamps.
- Exit code.
- Summary.
- Affected files.
- Events.
- Bounded logs.

---

## 11.6 Change 7.4 — Recovery

### Change

```text
recover-interrupted-executions
```

### Spec

```text
execution-recovery
```

### Requirements

- Detect unclosed executions.
- Mark as interrupted.
- Refresh workspace.
- Report possible inconsistency.
- Allow retry of operation.
- Do not assume a process is still alive.

### Phase Gate

- Every execution is visible.
- The application can restart without losing history.
- Secrets do not appear in records.

---

# 12. Phase 8 — Git, Security, and Recovery

## 12.1 Objective

Reduce the risk of an agent modifying a repository unsafely.

## 12.2 Exploration

```text
/opsx:explore
```

```text
Analyze the risks of allowing agents to modify a repository.

Design controls for:

- dirty working tree;
- branches;
- conflicts;
- checkpoints;
- sensitive files;
- worktrees;
- simultaneous processes;
- destructive actions;
- recovery;
- confirmations.
```

---

## 12.3 Change 8.1 — Git State

### Change

```text
inspect-git-workspace
```

### Spec

```text
git-workspace
```

### Requirements

- Detect repository.
- Show branch.
- Detect modified files.
- Detect conflicts.
- Show untracked files.
- Allow read-only mode without Git.

---

## 12.4 Change 8.2 — Pre-Execution Checks

### Change

```text
add-pre-execution-safety-checks
```

### Spec

```text
execution-safety
```

### Validations

- Valid project.
- Valid change.
- Available backend.
- Available credentials.
- Compatible operation.
- Occupied workspace.
- Dirty working tree.
- Sensitive files.
- Required confirmation.

---

## 12.5 Change 8.3 — Git Checkpoints

### Change

```text
add-git-checkpoints
```

### Spec

```text
git-checkpoints
```

### Requirements

- Offer checkpoint before `apply`.
- Show included files.
- Do not commit automatically.
- Record hash.
- Do not silently include files.
- Allow skipping checkpoint.

---

## 12.6 Change 8.4 — Worktrees per Change

### Change

```text
isolate-changes-with-git-worktrees
```

### Spec

```text
change-worktrees
```

### Requirements

- Create worktree.
- Associate branch and change.
- Execute agent within the worktree.
- Detect occupied worktree.
- Do not delete unsaved changes.
- Confirmed cleanup.

### Phase Gate

- Modifying executions show risks.
- The user can create a checkpoint.
- Git state is visible before and after execution.

---

# 13. Phase 9 — Distribution and Extensibility

## 13.1 Objective

Prepare OPSX TUI for installation, maintenance, and extensions.

## 13.2 Exploration

```text
/opsx:explore
```

```text
Explore how to distribute and extend OPSX TUI.

Consider:

- PyPI;
- pipx;
- semantic versioning;
- backend plugins;
- themes;
- diagnostics;
- compatibility;
- documentation;
- configuration migrations.

Avoid an overly complex plugin system.
```

---

## 13.3 Change 9.1 — Themes

### Change

```text
add-theme-system
```

### Spec

```text
tui-theming
```

---

## 13.4 Change 9.2 — Backend Plugins

### Change

```text
add-backend-plugin-registry
```

### Spec

```text
backend-plugins
```

---

## 13.5 Change 9.3 — Distribution

### Change

```text
package-opsx-tui-for-distribution
```

### Spec

```text
application-distribution
```

### Requirements

- PyPI publication.
- Installation with `pipx`.
- `opsx-tui` command.
- Semantic versioning.
- TCSS resources included.
- Python validation.
- `opsx-tui --version`.
- `opsx-tui doctor`.

---

## 13.6 Change 9.4 — Documentation

### Change

```text
add-user-documentation
```

### Spec

```text
user-documentation
```

### Contents

- Installation.
- First launch.
- Shortcuts.
- Configuration.
- Agents.
- Providers.
- Security.
- Troubleshooting.
- Plugin development.

---

# 14. Product Versions

## 14.1 Version 0.1 — OpenSpec Viewer

Includes:

```text
bootstrap-opsx-tui-project
discover-openspec-project
read-openspec-workspace
parse-openspec-tasks
add-application-shell
add-keyboard-navigation
add-markdown-preview
add-spec-browser
add-change-detail-screen
infer-change-lifecycle
add-kanban-board
watch-openspec-workspace
add-board-filtering
```

Result:

> Visualize OpenSpec projects, specs, changes, tasks, and states.

## 14.2 Version 0.2 — OpenSpec Controller

Includes:

```text
add-openspec-cli-adapter
add-command-catalog
add-command-palette
add-openspec-command-runner
add-execution-event-model
add-live-execution-console
persist-execution-history
```

Result:

> Execute local OpenSpec commands from the TUI.

## 14.3 Version 0.3 — OpenSpec Agent

Includes:

```text
define-agent-backend-contract
add-codex-cli-backend
execute-opsx-actions-through-agent
add-agent-profile-settings
add-pre-execution-safety-checks
inspect-git-workspace
```

Result:

> Execute OPSX actions via Codex CLI.

## 14.4 Version 0.4 — Professional Environment

Includes:

```text
add-secure-credential-storage
add-provider-registry
add-openai-compatible-provider
add-git-checkpoints
recover-interrupted-executions
isolate-changes-with-git-worktrees
add-backend-plugin-registry
add-theme-system
package-opsx-tui-for-distribution
```

Result:

> Secure, multi-agent, configurable, and distributable operation.

---

# 15. Prioritized Backlog

| Order | Change | Main Spec | Version |
|---:|---|---|---|
| 1 | `bootstrap-opsx-tui-project` | `project-foundation` | 0.1 |
| 2 | `discover-openspec-project` | `project-discovery` | 0.1 |
| 3 | `read-openspec-workspace` | `workspace-catalog` | 0.1 |
| 4 | `parse-openspec-tasks` | `task-tracking` | 0.1 |
| 5 | `add-application-shell` | `tui-shell` | 0.1 |
| 6 | `add-keyboard-navigation` | `keyboard-navigation` | 0.1 |
| 7 | `add-markdown-preview` | `markdown-preview` | 0.1 |
| 8 | `add-spec-browser` | `spec-browser` | 0.1 |
| 9 | `add-change-detail-screen` | `change-detail` | 0.1 |
| 10 | `infer-change-lifecycle` | `change-lifecycle` | 0.1 |
| 11 | `add-kanban-board` | `kanban-board` | 0.1 |
| 12 | `watch-openspec-workspace` | `workspace-monitoring` | 0.1 |
| 13 | `add-board-filtering` | `workspace-filtering` | 0.1 |
| 14 | `add-openspec-cli-adapter` | `openspec-cli` | 0.2 |
| 15 | `add-command-catalog` | `command-catalog` | 0.2 |
| 16 | `add-command-palette` | `command-palette` | 0.2 |
| 17 | `add-openspec-command-runner` | `command-execution` | 0.2 |
| 18 | `add-execution-event-model` | `execution-events` | 0.2 |
| 19 | `add-live-execution-console` | `execution-console` | 0.2 |
| 20 | `persist-execution-history` | `execution-history` | 0.2 |
| 21 | `define-agent-backend-contract` | `agent-backend` | 0.3 |
| 22 | `add-codex-cli-backend` | `codex-backend` | 0.3 |
| 23 | `execute-opsx-actions-through-agent` | `opsx-orchestration` | 0.3 |
| 24 | `add-agent-profile-settings` | `agent-configuration` | 0.3 |
| 25 | `inspect-git-workspace` | `git-workspace` | 0.3 |
| 26 | `add-pre-execution-safety-checks` | `execution-safety` | 0.3 |
| 27 | `recover-interrupted-executions` | `execution-recovery` | 0.4 |
| 28 | `add-git-checkpoints` | `git-checkpoints` | 0.4 |
| 29 | `add-secure-credential-storage` | `credential-management` | 0.4 |
| 30 | `add-provider-registry` | `llm-provider-registry` | 0.4 |
| 31 | `add-openai-compatible-provider` | `openai-compatible-provider` | 0.4 |
| 32 | `isolate-changes-with-git-worktrees` | `change-worktrees` | 0.4 |
| 33 | `add-theme-system` | `tui-theming` | 0.4 |
| 34 | `add-backend-plugin-registry` | `backend-plugins` | 0.4 |
| 35 | `package-opsx-tui-for-distribution` | `application-distribution` | 0.4 |
| 36 | `add-user-documentation` | `user-documentation` | 0.4 |

---

# 16. Expected Canonical Specs

Once changes have been archived, the expected structure will be similar to:

```text
openspec/
├── config.yaml
├── specs/
│   ├── project-foundation/
│   ├── project-discovery/
│   ├── workspace-catalog/
│   ├── task-tracking/
│   ├── workspace-monitoring/
│   ├── tui-shell/
│   ├── keyboard-navigation/
│   ├── markdown-preview/
│   ├── spec-browser/
│   ├── change-detail/
│   ├── change-lifecycle/
│   ├── kanban-board/
│   ├── change-metadata/
│   ├── workspace-filtering/
│   ├── openspec-cli/
│   ├── command-catalog/
│   ├── command-palette/
│   ├── command-execution/
│   ├── agent-backend/
│   ├── codex-backend/
│   ├── opsx-orchestration/
│   ├── agent-configuration/
│   ├── llm-provider-registry/
│   ├── openai-compatible-provider/
│   ├── credential-management/
│   ├── execution-events/
│   ├── execution-console/
│   ├── execution-history/
│   ├── execution-recovery/
│   ├── git-workspace/
│   ├── execution-safety/
│   ├── git-checkpoints/
│   ├── change-worktrees/
│   ├── tui-theming/
│   ├── backend-plugins/
│   ├── application-distribution/
│   └── user-documentation/
└── changes/
```

These folders must not be manually created at the start. They will be consolidated when each proposal is archived.

---

# 17. Persistence Policy

## 17.1 Data Owned by OpenSpec

- Specs.
- Requirements.
- Scenarios.
- Proposals.
- Design.
- Tasks.
- Task progress.
- Deltas.
- Active changes.
- Archived changes.
- Methodological configuration.

## 17.2 Data Owned by OPSX TUI

- Visual configuration.
- Recent projects.
- Selected backend.
- Selected model.
- Execution history.
- Logs.
- Durations.
- Exit codes.
- Filters.
- Auxiliary tags.
- Priorities.
- Local block reasons.
- Security preferences.
- Session state.

## 17.3 Data That Will Not Be Duplicated

- Spec content.
- Proposal content.
- Task content.
- Progress.
- Archived status.
- Computable methodological state.

---

# 18. Configuration System

## 18.1 Global Configuration

```text
Linux:
~/.config/opsx-tui/config.toml
```

Example:

```toml
schema_version = 1
default_backend = "codex"
theme = "opsx-dark"
editor = "code --wait"
history_retention_days = 90

[ui]
show_archived = false
compact_cards = false
mouse_support = true

[execution]
default_timeout_seconds = 1800
confirm_mutating_operations = true

[backends.codex]
type = "cli"
executable = "codex"
model = "default"
approval_mode = "confirm"
```

## 18.2 Per-Project Configuration

```text
<project>/.opsx-tui/config.toml
```

Example:

```toml
schema_version = 1

[project]
display_name = "OPSX TUI"

[operations.explore]
backend = "codex"

[operations.propose]
backend = "codex"

[operations.apply]
backend = "codex"
approval_mode = "confirm"

[git]
require_clean_tree_for_apply = false
offer_checkpoint = true
```

## 18.3 Precedence

```text
defaults
  < global configuration
  < project configuration
  < environment variables
  < CLI arguments
  < temporary session selection
```

---

# 19. Global Quality Criteria

Each change must meet:

- Unit tests.
- Integration tests where applicable.
- Ruff with no errors.
- MyPy with no critical errors.
- Compatibility with Python 3.11.
- Updated documentation.
- No direct UI access to infrastructure.
- No `shell=True`.
- No secrets in logs.
- No duplicating OpenSpec canonical data.
- Verifiable acceptance criteria.
- Satisfactory `/opsx:verify` result before archiving.

---

# 20. First Execution Sequence

## Step 1

Initialize OpenSpec:

```bash
openspec init
openspec config profile
openspec update
```

## Step 2

Explore the foundation:

```text
/opsx:explore
```

Use the instruction defined in Phase 0.

## Step 3

Create the first proposal:

```text
/opsx:propose bootstrap-opsx-tui-project
```

## Step 4

Apply:

```text
/opsx:apply bootstrap-opsx-tui-project
```

## Step 5

Verify:

```text
/opsx:verify bootstrap-opsx-tui-project
```

## Step 6

Archive:

```text
/opsx:archive bootstrap-opsx-tui-project
```

## Step 7

Continue with:

```text
discover-openspec-project
```

---

# 21. MVP Definition of Done

OPSX TUI 0.3 will be considered functional when it allows:

1. Opening an OpenSpec project.
2. Detecting its root.
3. Reading specs, changes, proposals, designs, and tasks.
4. Displaying a Kanban board.
5. Showing progress and inferred state.
6. Navigating via keyboard.
7. Viewing Markdown.
8. Executing OpenSpec commands.
9. Executing OPSX actions via Codex CLI.
10. Showing real-time output.
11. Canceling processes.
12. Maintaining history.
13. Showing Git state.
14. Applying security validations.
15. Executing the cycle:

```text
propose → apply → verify → archive
```

from a single terminal interface.

---

# 22. Conclusion

The construction of OPSX TUI must progress from a reading tool to an operating tool.

The recommended order is:

```text
Understand OpenSpec
        ↓
Represent OpenSpec
        ↓
Visualize OpenSpec
        ↓
Execute OpenSpec
        ↓
Orchestrate agents
        ↓
Secure executions
        ↓
Extend and distribute
```

The initial priority should be to build a reliable workspace model and a useful read-only interface. Agent and LLM provider execution should be incorporated only after the representation of specs, changes, tasks, and states is stable.
