# OPSX TUI

> Terminal control center to visualize, understand, and operate OpenSpec projects.

OPSX TUI is a TUI application built in Python with Textual. It allows exploring specs, reviewing changes, visualizing tasks and states on a Kanban board, executing OpenSpec commands, and delegating OPSX actions to configured agents, keeping the user in control before, during, and after each execution.

```text
┌─ OPSX TUI ────────────────────────────────────────────────────────────────┐
│ [1] Board  [2] Specs  [3] Changes  [4] Runner  [5] Logs  [6] Settings   │
├───────────────────────────────────────────────────────────────────────────┤
│ DRAFT        PLANNING       READY          APPLYING       VERIFICATION   │
│                                                                           │
│ auth-sso     stock-api      new-theme      payments       cache-v2       │
│ 0/0 tasks    artifacts 2/4  0/12 tasks     7/11 tasks     11/11 tasks    │
│                                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│ Change: payments                                                          │
│ Proposal ✓  Design ✓  Delta Specs ✓  Tasks 7/11  Verification —          │
├───────────────────────────────────────────────────────────────────────────┤
│ enter open  a apply  v verify  Ctrl+P commands  ? help  q quit           │
└───────────────────────────────────────────────────────────────────────────┘
```

## Project status

OPSX TUI is in the design and incremental construction stage via OpenSpec.

Development is organized through the cycle:

```text
explore → propose → apply → verify → archive
```

Implementation is divided into small, verifiable changes. Each change must meet the Definition of Done before archiving.

## Objectives

OPSX TUI must allow:

- detecting and opening an OpenSpec project;
- exploring canonical specs;
- reviewing active and archived changes;
- visualizing proposals, designs, tasks, and delta specs;
- calculating and explaining the lifecycle of each change;
- displaying changes on a Kanban board;
- executing local OpenSpec commands;
- executing OPSX actions through agents;
- configuring backends and models;
- observing processes in real time;
- canceling executions;
- maintaining history;
- inspecting Git;
- applying security controls.

## Principles

### OpenSpec is the source of truth

OPSX TUI does not create a parallel methodological system.

OpenSpec maintains authority over:

- specs;
- proposals;
- designs;
- tasks;
- delta specs;
- active changes;
- archived changes.

OPSX TUI maintains only operational information:

- visual configuration;
- backends;
- models;
- history;
- logs;
- filters;
- auxiliary metadata;
- security policies.

### State must be explainable

Each Kanban state must be accompanied by evidence.

```text
State: applying

Reasons:
- proposal.md available.
- design.md available.
- delta specs available.
- 7 of 11 tasks completed.
```

### The user maintains control

Before a modifying operation, OPSX TUI must display:

- project;
- change;
- action;
- backend;
- model;
- sandbox;
- permissions;
- Git status;
- risks.

### Security by default

The project prohibits:

- `shell=True`;
- secrets in TOML;
- writes outside the workspace without authorization;
- archive without current verification;
- duplication of OpenSpec canonical data;
- domain logic inside widgets.

## Architecture

OPSX TUI uses a lightweight hexagonal architecture:

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

Architectural rules:

- Presentation does not access the filesystem directly.
- Presentation does not execute subprocesses.
- Domain does not depend on Textual.
- Infrastructure implements ports.
- Workspace snapshots are immutable.
- Lifecycle rules live in Domain/Application.
- Backends are modeled by capabilities.

## Technology stack

| Area | Technology |
|---|---|
| Language | Python 3.11–3.14 |
| TUI framework | Textual |
| Styles | TCSS |
| Models | Pydantic 2 |
| Concurrency | asyncio |
| Processes | `asyncio.create_subprocess_exec` |
| Filesystem watcher | watchfiles |
| Configuration | TOML |
| User paths | platformdirs |
| Persistence | SQLite |
| Secrets | keyring or environment variables |
| Testing | Pytest, pytest-asyncio, Hypothesis |
| Quality | Ruff, MyPy |

## Requirements

- Python 3.11 or higher.
- OpenSpec installed for CLI operations.
- A compatible agent for OPSX actions.
- Git recommended for modifying operations.

Read mode should continue working even if OpenSpec CLI, Git, or an agent are not available.

## Installation

The project has not yet published a stable version.

When a distributable package exists:

```bash
pipx install opsx-tui
```

For development:

```bash
git clone <repository-url>
cd opsx-tui

python3.11 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Execution

From the root of an OpenSpec project:

```bash
opsx-tui
```

With an explicit path:

```bash
opsx-tui --project /path/to/project
```

Via environment variable:

```bash
OPSX_TUI_PROJECT=/path/to/project opsx-tui
```

## Project detection

OPSX TUI searches for the root in this order:

```text
1. --project
2. OPSX_TUI_PROJECT
3. upward search from cwd
4. Git root
5. recent projects
6. interactive selection
```

The tool does not run `openspec init` automatically.

## Main views

### Board

Kanban board with changes grouped by lifecycle:

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

### Specs

Explorer for canonical specs, requirements, and scenarios.

### Changes

List of active and archived changes.

### Change Detail

Consolidated view of:

- proposal;
- design;
- delta specs;
- tasks;
- lifecycle;
- verifications;
- executions;
- Git;
- diagnostics.

### Runner

Execution center for commands and OPSX actions.

### Logs

History of executions, events, and results.

### Settings

Global and per-project configuration.

## Initial shortcuts

| Key | Action |
|---|---|
| `1` | Board |
| `2` | Specs |
| `3` | Changes |
| `4` | Runner |
| `5` | Logs |
| `6` | Settings |
| `Ctrl+P` | Command palette |
| `/` | Search |
| `r` | Refresh |
| `g` | Change project |
| `?` | Help |
| `q` | Quit |
| `Esc` | Close modal |

## Integration with OpenSpec

OPSX TUI distinguishes three layers:

```text
FILESYSTEM
Persistent content

CLI OPENSPEC
State, validation, and official commands

AGENT BACKEND
OPSX actions and assisted work
```

Do not confuse:

```text
openspec <command>
```

with:

```text
/opsx:<action>
```

Actual syntax and capabilities are detected based on the installed version and configured backend.

## Backends

The first target backend is Codex CLI.

The architecture must allow adding:

- Claude Code;
- Gemini CLI;
- other agents;
- OpenAI-compatible providers in later phases.

Each backend declares capabilities such as:

- streaming;
- cancellation;
- model selection;
- sandbox;
- approvals;
- network access;
- workspace write access.

## Configuration

### Global

Linux:

```text
~/.config/opsx-tui/config.toml
```

Example:

```toml
schema_version = 1
default_backend = "codex"
theme = "opsx-dark"
editor = "code --wait"

[execution]
default_timeout_seconds = 1800
confirm_mutating_operations = true

[backends.codex]
type = "codex-cli"
executable = "codex"
model = "default"
approval_mode = "confirm"
sandbox_mode = "workspace-write"
```

### Per project

```text
<project>/.opsx-tui/config.toml
```

Project configuration cannot relax mandatory global policies.

### Precedence

```text
defaults
< global
< project
< environment
< CLI
< session
```

### Secrets

Secrets must be obtained from:

- keyring;
- environment variables;
- agent authentication.

They must never be stored in TOML or SQLite.

## Development with OpenSpec

Each capability must be built as an independent change.

Recommended flow:

```text
/opsx:explore
/opsx:propose
/opsx:apply
/opsx:verify
/opsx:archive
```

Initial example:

```text
bootstrap-opsx-tui-project
```

Then:

```text
discover-openspec-project
read-openspec-workspace
parse-openspec-tasks
add-application-shell
add-spec-browser
infer-change-lifecycle
add-kanban-board
```

The complete roadmap is in `docs/01-construction-plan.md`.

## Roadmap

### 0.1 — OpenSpec Viewer

- discovery;
- workspace;
- tasks;
- TUI shell;
- specs;
- changes;
- lifecycle;
- Kanban;
- watcher.

### 0.2 — OpenSpec Controller

- CLI adapter;
- command catalog;
- palette;
- runner;
- events;
- history.

### 0.3 — OpenSpec Agent

- backend contract;
- Codex CLI;
- OPSX actions;
- profiles;
- security;
- Git.

### 0.4 — Professional Environment

- providers;
- credentials;
- recovery;
- checkpoints;
- worktrees;
- plugins;
- distribution.

## Expected structure

```text
opsx-tui/
├── pyproject.toml
├── README.md
├── docs/
├── openspec/
├── src/
│   └── opsx_tui/
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       └── presentation/
└── tests/
    ├── unit/
    ├── contract/
    ├── integration/
    ├── tui/
    ├── e2e/
    └── fixtures/
```

## Quality

Before archiving a change, the following must pass:

```bash
ruff check .
mypy src
pytest
```

The CI matrix must cover:

```text
Python 3.11
Python 3.12
Python 3.13
Python 3.14
```

Python 3.11 is the minimum mandatory gate.

## Definition of Done

A change can only be considered complete if:

- all requirements are implemented;
- all scenarios are covered;
- tasks reflect real work;
- tests exist;
- Ruff passes;
- MyPy passes;
- Pytest passes;
- Python 3.11 passes;
- documentation is up to date;
- no critical findings exist;
- `/opsx:verify` is current;
- the change is ready for archive.

See `docs/10-definition-of-done.md`.

## Security

Mandatory rules:

- never use shell;
- validate paths;
- detect external symlinks;
- redact secrets;
- filter environment variables;
- confirm modifying operations;
- display real sandbox;
- inspect Git;
- limit concurrency;
- functionally validate results.

See `docs/07-security-model.md`.

## Documentation

The `docs/` folder contains the project's normative context:

| Document | Contents |
|---|---|
| `01-construction-plan.md` | Phases, changes, and roadmap |
| `02-product-contract.md` | Functional contract |
| `03-domain-model.md` | Domain model and glossary |
| `04-openspec-integration-contract.md` | Integration with OpenSpec |
| `05-change-lifecycle-rules.md` | States and Kanban |
| `06-agent-backend-contract.md` | Agent backends |
| `07-security-model.md` | Security |
| `08-testing-strategy.md` | Testing strategy |
| `09-architecture-decision-records.md` | ADR |
| `10-definition-of-done.md` | Definition of Done |

## Contributing

Before implementing:

1. Review the functional contract.
2. Review the current OpenSpec specs.
3. Confirm the active change.
4. Review related ADRs.
5. Limit work to the scope.
6. Create or update tests.
7. Run the gates.
8. Update documentation.
9. Run `/opsx:verify`.
10. Archive only if the DoD is met.

## Rules for agents

Agents must not:

- expand scope without authorization;
- introduce major dependencies without an ADR;
- silently change architecture;
- mark tasks without evidence;
- declare success by text;
- duplicate OpenSpec in SQLite;
- store secrets;
- use shell;
- skip Python 3.11;
- archive with stale verification.

The close report must include:

```text
Change:
Objective:
Requirements implemented:
Files modified:
Tests:
Quality:
Security:
Documentation:
Verify result:
Blockers:
Registered debt:
Recommended state:
```

## License

The project's license has yet to be defined.

Until an explicit license exists, redistribution permission must not be assumed.

## Name

```text
Product: OPSX TUI
Distribution: opsx-tui
Python package: opsx_tui
Command: opsx-tui
```
